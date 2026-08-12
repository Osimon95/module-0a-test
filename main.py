import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import uuid

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R18"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# WEEX CREDENTIALS
# ============================================================
#
# IMPORTANT:
#
# Render must contain EXACTLY:
#
# WEEX_API_KEY
# WEEX_API_SECRET
# WEEX_API_PASSPHRASE
#
# Do NOT use:
#
# WEEX_SECRET_KEY
# WEEX_PASSPHRASE
#
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
# TP / TRAILING CONFIG
# ============================================================

TP1_SIZE_PERCENT = Decimal(
    os.getenv(
        "TP1_SIZE_PERCENT",
        "20",
    )
)

TP2_SIZE_PERCENT = Decimal(
    os.getenv(
        "TP2_SIZE_PERCENT",
        "20",
    )
)

TP3_SIZE_PERCENT = Decimal(
    os.getenv(
        "TP3_SIZE_PERCENT",
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
        "180",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)


# ============================================================
# ABSOLUTE REAL-ORDER SAFETY LOCK
# ============================================================
#
# R18 IS NOT ALLOWED TO SEND REAL ORDERS.
#
# There is deliberately no real-order POST call in this file.
#
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_REAL_ORDER_LOCK = True


# ============================================================
# DEMO ORDER CONFIG
# ============================================================
#
# R18 may transmit ONE DEMO/PAPER order only.
#
# /capi/v3/sim/order
#
# This cannot be changed into /capi/v3/order through ENV.
#
# ============================================================

DEMO_ORDER_ENABLED = True

DEMO_ORDER_PATH = "/capi/v3/sim/order"

REAL_ORDER_PATH = "/capi/v3/order"


# ============================================================
# CONSTANTS
# ============================================================

ZERO = Decimal("0")

ONE_HUNDRED = Decimal("100")

HTTP_TIMEOUT = aiohttp.ClientTimeout(
    total=20,
)

USER_AGENT = (
    "0F-4H-R18-WEEX-DIAGNOSTIC"
)


# ============================================================
# RUNTIME FLAGS
# ============================================================

real_post_called = False

demo_post_attempted = False

demo_post_success = False

telegram_sent = False


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def fmt(value):
    if isinstance(value, Decimal):
        text = format(
            value.normalize(),
            "f",
        )

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text or "0"

    return str(value)


def yes_no(value):
    return (
        "✅ YES"
        if value
        else "❌ NO"
    )


def mask_secret(value):
    if not value:
        return "MISSING"

    if len(value) <= 8:
        return "SET"

    return (
        value[:4]
        + "..."
        + value[-4:]
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
            "Missing WEEX credentials: "
            + ", ".join(missing)
        )

    return True


# ============================================================
# CONFIG VALIDATION
# ============================================================

def validate_configuration():

    if INITIAL_ENTRY_PERCENT <= ZERO:
        raise RuntimeError(
            "INITIAL_ENTRY_PERCENT must be > 0"
        )

    if LEVERAGE <= ZERO:
        raise RuntimeError(
            "LEVERAGE must be > 0"
        )

    if MAX_LEVERAGE <= ZERO:
        raise RuntimeError(
            "MAX_LEVERAGE must be > 0"
        )

    if LEVERAGE > MAX_LEVERAGE:
        raise RuntimeError(
            f"Configured leverage {fmt(LEVERAGE)}x "
            f"exceeds MAX_LEVERAGE "
            f"{fmt(MAX_LEVERAGE)}x"
        )

    if MAX_PYRAMID_ADDS < 0:
        raise RuntimeError(
            "MAX_PYRAMID_ADDS cannot be negative"
        )

    if MAX_BACKUPS < 0:
        raise RuntimeError(
            "MAX_BACKUPS cannot be negative"
        )

    total_exposure = (
        INITIAL_ENTRY_PERCENT
        + (
            PYRAMID_SIZE_PERCENT
            * MAX_PYRAMID_ADDS
        )
        + (
            BACKUP_SIZE_PERCENT
            * MAX_BACKUPS
        )
    )

    if total_exposure > MAX_FUND_EXPOSURE_PERCENT:
        raise RuntimeError(
            "Worst-case exposure "
            f"{fmt(total_exposure)}% exceeds "
            "MAX_FUND_EXPOSURE_PERCENT "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        )

    tp_total = (
        TP1_SIZE_PERCENT
        + TP2_SIZE_PERCENT
        + TP3_SIZE_PERCENT
    )

    if tp_total != ONE_HUNDRED:
        raise RuntimeError(
            "TP allocation must equal 100%. "
            f"Current total: {fmt(tp_total)}%"
        )

    if HARD_REAL_ORDER_LOCK is not True:
        raise RuntimeError(
            "R18 HARD_REAL_ORDER_LOCK must be TRUE"
        )

    if LIVE_ORDER_EXECUTION is not False:
        raise RuntimeError(
            "R18 LIVE_ORDER_EXECUTION must be FALSE"
        )

    return total_exposure


# ============================================================
# JSON SERIALIZATION
# ============================================================

def compact_json(data):
    return json.dumps(
        data,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


# ============================================================
# WEEX V3 SIGNATURE
# ============================================================

def create_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body_string="",
):
    method = method.upper()

    if query_string:
        message = (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body_string
        )
    else:
        message = (
            str(timestamp)
            + method
            + request_path
            + body_string
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


def create_private_headers(
    method,
    request_path,
    query_string="",
    body_string="",
):
    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    signature = create_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body_string=body_string,
    )

    return {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "User-Agent":
            USER_AGENT,
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
        timeout=HTTP_TIMEOUT,
        headers={
            "User-Agent":
                USER_AGENT,
        },
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(text)
        except Exception:
            raise RuntimeError(
                "Unable to decode WEEX "
                f"public response: {text}"
            )


# ============================================================
# GENERIC PRIVATE GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):
    params = params or {}

    query_string = urlencode(
        params
    )

    headers = create_private_headers(
        method="GET",
        request_path=path,
        query_string=query_string,
        body_string="",
    )

    url = (
        API_BASE_URL
        + path
    )

    if query_string:
        url += (
            "?"
            + query_string
        )

    async with session.get(
        url,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE GET HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(text)
        except Exception:
            raise RuntimeError(
                "Unable to decode WEEX "
                f"private GET response: "
                f"{text}"
            )


# ============================================================
# DEMO POST ONLY
# ============================================================

async def demo_post(
    session,
    path,
    payload,
):
    global demo_post_attempted
    global demo_post_success

    # --------------------------------------------------------
    # ABSOLUTE PATH CHECK
    # --------------------------------------------------------

    if path != DEMO_ORDER_PATH:
        raise RuntimeError(
            "R18 blocked POST path: "
            f"{path}"
        )

    if path == REAL_ORDER_PATH:
        raise RuntimeError(
            "ABSOLUTE REAL ORDER POST LOCK"
        )

    if not path.startswith(
        "/capi/v3/sim/"
    ):
        raise RuntimeError(
            "R18 permits DEMO POST "
            "paths only"
        )

    body_string = compact_json(
        payload
    )

    headers = create_private_headers(
        method="POST",
        request_path=path,
        query_string="",
        body_string=body_string,
    )

    url = (
        API_BASE_URL
        + path
    )

    demo_post_attempted = True

    async with session.post(
        url,
        data=body_string,
        headers=headers,
        timeout=HTTP_TIMEOUT,
    ) as response:

        text = await response.text()

        try:
            decoded = json.loads(
                text
            )
        except Exception:
            decoded = {
                "raw": text
            }

        if response.status != 200:
            raise RuntimeError(
                f"WEEX DEMO POST HTTP "
                f"{response.status}: "
                f"{text}"
            )

        # WEEX may return HTTP 200 while
        # success=false inside the JSON.

        if isinstance(
            decoded,
            dict,
        ):
            if (
                "success" in decoded
                and
                decoded.get(
                    "success"
                ) is False
            ):
                raise RuntimeError(
                    "WEEX DEMO ORDER "
                    "REJECTED: "
                    + compact_json(
                        decoded
                    )
                )

        demo_post_success = True

        return decoded


# ============================================================
# ABSOLUTE REAL POST TRAP
# ============================================================

async def real_order_post_trap(
    *args,
    **kwargs,
):
    global real_post_called

    real_post_called = True

    raise RuntimeError(
        "R18 ABSOLUTE REAL-ORDER "
        "POST LOCK TRIGGERED"
    )


# ============================================================
# API TRADING SYMBOL CHECK
# ============================================================

async def get_api_trading_symbols(
    session,
):
    path = (
        "/capi/v3/market/"
        "apiTradingSymbols"
    )

    data = await public_get(
        session,
        path,
    )

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "symbols",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                data = value
                break

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected API trading "
            "symbols response"
        )

    normalized = []

    for item in data:
        if isinstance(
            item,
            str,
        ):
            normalized.append(
                item.upper()
            )

        elif isinstance(
            item,
            dict,
        ):
            value = item.get(
                "symbol"
            )

            if value:
                normalized.append(
                    str(
                        value
                    ).upper()
                )

    return normalized


# ============================================================
# EXCHANGE INFORMATION
# ============================================================

async def get_exchange_info(
    session,
):
    path = (
        "/capi/v3/market/"
        "exchangeInfo"
    )

    params = {
        "symbol":
            SYMBOL,
    }

    return await public_get(
        session,
        path,
        params=params,
    )


# ============================================================
# CONTRACT EXTRACTION
# ============================================================

def locate_contract_object(
    data,
):
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
            "symbols",
            "contracts",
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
                value,
                list,
            ):
                candidates.extend(
                    value
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

        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).upper()

        if (
            not symbol
            or symbol == SYMBOL
        ):
            return item

    raise RuntimeError(
        "Unable to locate contract "
        f"information for {SYMBOL}"
    )


def extract_contract_values(
    contract,
):
    min_qty = None
    qty_precision = None
    max_leverage = None
    min_leverage = None

    min_keys = (
        "minOrderQty",
        "minOrderQuantity",
        "minQty",
        "minTradeAmount",
        "minOrderSize",
    )

    precision_keys = (
        "quantityPrecision",
        "qtyPrecision",
        "volumePrecision",
    )

    max_lev_keys = (
        "maxLeverage",
        "max_leverage",
    )

    min_lev_keys = (
        "minLeverage",
        "min_leverage",
    )

    for key in min_keys:
        if key in contract:
            value = safe_decimal(
                contract[key]
            )

            if value > ZERO:
                min_qty = value
                break

    for key in precision_keys:
        if key in contract:
            try:
                qty_precision = int(
                    contract[key]
                )
                break
            except Exception:
                pass

    for key in max_lev_keys:
        if key in contract:
            value = safe_decimal(
                contract[key]
            )

            if value > ZERO:
                max_leverage = value
                break

    for key in min_lev_keys:
        if key in contract:
            value = safe_decimal(
                contract[key]
            )

            if value > ZERO:
                min_leverage = value
                break

    # Known BTC test baseline fallback.
    #
    # Only used when the exchange response
    # does not expose a field directly.

    if min_qty is None:
        min_qty = Decimal(
            "0.0001"
        )

    if qty_precision is None:
        qty_precision = 4

    if min_leverage is None:
        min_leverage = Decimal(
            "1"
        )

    if max_leverage is None:
        max_leverage = Decimal(
            "400"
        )

    return (
        min_qty,
        qty_precision,
        min_leverage,
        max_leverage,
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):
    paths = [
        (
            "/capi/v3/market/"
            "symbolPrice"
        ),
        (
            "/capi/v3/market/"
            "ticker"
        ),
    ]

    last_error = None

    for path in paths:

        try:
            data = await public_get(
                session,
                path,
                params={
                    "symbol":
                        SYMBOL,
                },
            )

            price = extract_mark_price(
                data
            )

            if price > ZERO:
                return price

        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "Unable to obtain mark price: "
        f"{last_error}"
    )


def extract_mark_price(
    ticker,
):
    objects = []

    if isinstance(
        ticker,
        list,
    ):
        objects.extend(
            ticker
        )

    elif isinstance(
        ticker,
        dict,
    ):
        objects.append(
            ticker
        )

        for key in (
            "data",
            "result",
        ):
            value = ticker.get(
                key
            )

            if isinstance(
                value,
                dict,
            ):
                objects.append(
                    value
                )

            elif isinstance(
                value,
                list,
            ):
                objects.extend(
                    value
                )

    for obj in objects:
        if not isinstance(
            obj,
            dict,
        ):
            continue

        for key in (
            "markPrice",
            "price",
            "lastPrice",
            "last",
            "close",
        ):
            if key in obj:
                price = safe_decimal(
                    obj[key]
                )

                if price > ZERO:
                    return price

    raise RuntimeError(
        "Unable to extract mark price"
    )


# ============================================================
# REAL POSITION CHECK
# ============================================================

async def get_real_positions(
    session,
):
    path = (
        "/capi/v3/account/"
        "position/allPosition"
    )

    data = await private_get(
        session,
        path,
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

    return []


def find_open_symbol_positions(
    positions,
):
    result = []

    for position in positions:
        if not isinstance(
            position,
            dict,
        ):
            continue

        if str(
            position.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:
            continue

        size = safe_decimal(
            position.get(
                "size",
                position.get(
                    "quantity",
                    "0",
                ),
            )
        )

        if size != ZERO:
            result.append(
                position
            )

    return result


# ============================================================
# QUANTITY CALCULATION
# ============================================================

def quantity_step(
    precision,
):
    return Decimal(
        "1"
    ).scaleb(
        -precision
    )


def calculate_quantity(
    balance,
    mark_price,
    precision,
):
    margin = (
        balance
        * INITIAL_ENTRY_PERCENT
        / ONE_HUNDRED
    )

    notional = (
        margin
        * LEVERAGE
    )

    raw_quantity = (
        notional
        / mark_price
    )

    step = quantity_step(
        precision
    )

    quantity = raw_quantity.quantize(
        step,
        rounding=ROUND_DOWN,
    )

    return (
        margin,
        notional,
        quantity,
    )


# ============================================================
# DEMO BALANCE
# ============================================================

async def get_demo_balance(
    session,
):
    path = (
        "/capi/v3/sim/balance"
    )

    data = await private_get(
        session,
        path,
    )

    if isinstance(
        data,
        list,
    ):
        assets = data

    elif isinstance(
        data,
        dict,
    ):
        assets = None

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
                assets = value
                break

        if assets is None:
            assets = [
                data
            ]

    else:
        assets = []

    for asset in assets:
        if not isinstance(
            asset,
            dict,
        ):
            continue

        name = str(
            asset.get(
                "asset",
                asset.get(
                    "coin",
                    "",
                ),
            )
        ).upper()

        if name in (
            "SUSDT",
            "USDT",
        ):
            for key in (
                "availableBalance",
                "available",
                "balance",
            ):
                if key in asset:
                    value = safe_decimal(
                        asset[key]
                    )

                    if value >= ZERO:
                        return value

    raise RuntimeError(
        "Unable to extract demo balance"
    )


# ============================================================
# DEMO ORDER PAYLOAD
# ============================================================

def create_demo_order_payload(
    quantity,
):
    client_id = (
        "r18-"
        + uuid.uuid4().hex[:20]
    )

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
            fmt(quantity),

        "newClientOrderId":
            client_id,
    }


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):
    global telegram_sent

    if telegram_sent:
        return False

    if (
        not TELEGRAM_BOT_TOKEN
        or
        not TELEGRAM_CHAT_ID
    ):
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
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=HTTP_TIMEOUT,
        ) as response:

            await response.text()

            if response.status == 200:
                telegram_sent = True
                return True

    except Exception as exc:
        print(
            "TELEGRAM ERROR:",
            repr(exc),
        )

    return False


# ============================================================
# HEALTH SERVER
# ============================================================

async def health_handler(
    reader,
    writer,
):
    try:
        await reader.read(
            1024
        )

        body = (
            f"{MODULE_NAME} ACTIVE\n"
        ).encode(
            "utf-8"
        )

        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Connection: close\r\n"
            b"Content-Length: "
            + str(
                len(body)
            ).encode()
            + b"\r\n\r\n"
            + body
        )

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
    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    server = await asyncio.start_server(
        health_handler,
        host="0.0.0.0",
        port=port,
    )

    print(
        f"HEALTH SERVER ACTIVE "
        f"ON PORT {port}"
    )

    return server


# ============================================================
# REPORT BUILDERS
# ============================================================

def build_success_report(
    api_symbol_allowed,
    mark_price,
    demo_balance,
    min_order,
    qty_precision,
    weex_min_leverage,
    weex_max_leverage,
    demo_margin,
    demo_notional,
    demo_quantity,
    total_exposure,
    open_real_positions,
    demo_result,
):
    position_clear = (
        len(
            open_real_positions
        )
        == 0
    )

    leverage_gate = (
        LEVERAGE
        >= weex_min_leverage
        and
        LEVERAGE
        <= weex_max_leverage
        and
        LEVERAGE
        <= MAX_LEVERAGE
    )

    quantity_positive = (
        demo_quantity
        > ZERO
    )

    minimum_passed = (
        demo_quantity
        >= min_order
    )

    lines = [
        (
            f"✅ MODULE "
            f"{MODULE_NAME} "
            "DIAGNOSTIC PASSED"
        ),

        SYMBOL,

        "",

        "CREDENTIAL CONFIG",

        (
            "WEEX_API_KEY: "
            + mask_secret(
                WEEX_API_KEY
            )
        ),

        (
            "WEEX_API_SECRET: "
            + (
                "✅ SET"
                if WEEX_API_SECRET
                else "❌ MISSING"
            )
        ),

        (
            "WEEX_API_PASSPHRASE: "
            + (
                "✅ SET"
                if WEEX_API_PASSPHRASE
                else "❌ MISSING"
            )
        ),

        "",

        "FINAL EXECUTION GATE",

        (
            "API Trading Symbol: "
            + yes_no(
                api_symbol_allowed
            )
        ),

        (
            "External Real Position Clear: "
            + yes_no(
                position_clear
            )
        ),

        "",

        "ADJUSTABLE CONFIG",

        (
            f"Entry: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%"
        ),

        (
            f"Leverage: "
            f"{fmt(LEVERAGE)}x"
        ),

        (
            f"Max Config Leverage: "
            f"{fmt(MAX_LEVERAGE)}x"
        ),

        "Margin Type: ISOLATED",

        (
            f"Max Pyramids: "
            f"{MAX_PYRAMID_ADDS}"
        ),

        (
            f"Pyramid Size: "
            f"{fmt(PYRAMID_SIZE_PERCENT)}%"
        ),

        (
            f"Max Backups: "
            f"{MAX_BACKUPS}"
        ),

        (
            f"Backup Size: "
            f"{fmt(BACKUP_SIZE_PERCENT)}% each"
        ),

        (
            f"Backup Buffer: "
            f"{fmt(BACKUP_BUFFER_PERCENT)}%"
        ),

        (
            f"Min Liq Distance: "
            f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%"
        ),

        (
            f"Max Fund Exposure: "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),

        (
            f"Worst-Case Exposure: "
            f"{fmt(total_exposure)}%"
        ),

        "",

        "WEEX CONTRACT",

        (
            f"Mark Price: "
            f"{fmt(mark_price)} USDT"
        ),

        (
            f"Minimum Order: "
            f"{fmt(min_order)}"
        ),

        (
            f"Quantity Precision: "
            f"{qty_precision}"
        ),

        (
            f"WEEX Min Leverage: "
            f"{fmt(weex_min_leverage)}x"
        ),

        (
            f"WEEX Max Leverage: "
            f"{fmt(weex_max_leverage)}x"
        ),

        (
            "Leverage Gate: "
            + yes_no(
                leverage_gate
            )
        ),

        "",

        "DEMO ACCOUNT",

        (
            f"Available Demo Balance: "
            f"{fmt(demo_balance)}"
        ),

        (
            f"Demo Entry Margin: "
            f"{fmt(demo_margin)}"
        ),

        (
            f"Demo Notional: "
            f"{fmt(demo_notional)}"
        ),

        (
            f"Demo Quantity: "
            f"{fmt(demo_quantity)}"
        ),

        (
            "Quantity Positive: "
            + yes_no(
                quantity_positive
            )
        ),

        (
            "Minimum Passed: "
            + yes_no(
                minimum_passed
            )
        ),

        "",

        "R18 DEMO TRANSMISSION",

        (
            "Demo POST Attempted: "
            + yes_no(
                demo_post_attempted
            )
        ),

        (
            "Demo POST Accepted: "
            + yes_no(
                demo_post_success
            )
        ),

        (
            "Real POST Called: "
            + (
                "🚨 YES"
                if real_post_called
                else "✅ NO"
            )
        ),

        (
            "Demo Endpoint: "
            f"{DEMO_ORDER_PATH}"
        ),

        "",

        "DEMO RESPONSE",

        compact_json(
            demo_result
        ),

        "",

        (
            "🛡 R18 absolute "
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

    return "\n".join(
        lines
    )


def build_error_report(
    stage,
    exc,
):
    return "\n".join(
        [
            (
                f"❌ MODULE "
                f"{MODULE_NAME} ERROR"
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

            (
                "Real POST Called: "
                + (
                    "🚨 YES"
                    if real_post_called
                    else "❌ NO"
                )
            ),

            (
                "Demo POST Attempted: "
                + yes_no(
                    demo_post_attempted
                )
            ),

            (
                "Demo POST Accepted: "
                + yes_no(
                    demo_post_success
                )
            ),

            (
                "🛡 R18 absolute "
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
# R18 MAIN DIAGNOSTIC
# ============================================================

async def run_r18():

    stage = (
        "startup"
    )

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} STARTING"
    )

    print(
        "CORRECTED WEEX V3 "
        "DEMO-ORDER TRANSMISSION TEST"
    )

    print(
        "ABSOLUTE REAL-ORDER "
        "POST LOCK ACTIVE"
    )

    print(
        "=" * 60
    )

    async with aiohttp.ClientSession() as session:

        try:
            # ================================================
            # CONFIGURATION
            # ================================================

            stage = (
                "configuration"
            )

            validate_credentials()

            total_exposure = (
                validate_configuration()
            )

            # ================================================
            # API TRADING SYMBOL
            # ================================================

            stage = (
                "API trading symbol"
            )

            api_symbols = (
                await get_api_trading_symbols(
                    session
                )
            )

            api_symbol_allowed = (
                SYMBOL
                in api_symbols
            )

            if not api_symbol_allowed:
                raise RuntimeError(
                    f"{SYMBOL} is not currently "
                    "listed as a WEEX API "
                    "trading symbol"
                )

            # ================================================
            # CONTRACT INFORMATION
            # ================================================

            stage = (
                "contract information"
            )

            exchange_info = (
                await get_exchange_info(
                    session
                )
            )

            contract = (
                locate_contract_object(
                    exchange_info
                )
            )

            (
                min_order,
                qty_precision,
                weex_min_leverage,
                weex_max_leverage,
            ) = extract_contract_values(
                contract
            )

            # ================================================
            # LEVERAGE GATE
            # ================================================

            stage = (
                "leverage gate"
            )

            if (
                LEVERAGE
                < weex_min_leverage
            ):
                raise RuntimeError(
                    f"{fmt(LEVERAGE)}x "
                    "is below WEEX minimum "
                    f"{fmt(weex_min_leverage)}x"
                )

            if (
                LEVERAGE
                > weex_max_leverage
            ):
                raise RuntimeError(
                    f"{fmt(LEVERAGE)}x "
                    "exceeds WEEX maximum "
                    f"{fmt(weex_max_leverage)}x"
                )

            # ================================================
            # MARK PRICE
            # ================================================

            stage = (
                "mark price"
            )

            mark_price = (
                await get_mark_price(
                    session
                )
            )

            # ================================================
            # REAL POSITION READ-ONLY CHECK
            # ================================================

            stage = (
                "real position read"
            )

            real_positions = (
                await get_real_positions(
                    session
                )
            )

            open_real_positions = (
                find_open_symbol_positions(
                    real_positions
                )
            )

            # ================================================
            # DEMO BALANCE
            # ================================================

            stage = (
                "demo balance"
            )

            demo_balance = (
                await get_demo_balance(
                    session
                )
            )

            # ================================================
            # DEMO SIZING
            # ================================================

            stage = (
                "demo sizing"
            )

            (
                demo_margin,
                demo_notional,
                demo_quantity,
            ) = calculate_quantity(
                balance=demo_balance,
                mark_price=mark_price,
                precision=qty_precision,
            )

            if demo_quantity <= ZERO:
                raise RuntimeError(
                    "Calculated demo "
                    "quantity is zero"
                )

            if (
                demo_quantity
                < min_order
            ):
                raise RuntimeError(
                    "Calculated demo quantity "
                    f"{fmt(demo_quantity)} "
                    "is below minimum order "
                    f"{fmt(min_order)}"
                )

            # ================================================
            # ABSOLUTE REAL ORDER ASSERTIONS
            # ================================================

            stage = (
                "real-order safety gate"
            )

            if LIVE_ORDER_EXECUTION:
                raise RuntimeError(
                    "LIVE_ORDER_EXECUTION "
                    "unexpectedly enabled"
                )

            if not HARD_REAL_ORDER_LOCK:
                raise RuntimeError(
                    "HARD_REAL_ORDER_LOCK "
                    "unexpectedly disabled"
                )

            if (
                DEMO_ORDER_PATH
                == REAL_ORDER_PATH
            ):
                raise RuntimeError(
                    "Demo and real order "
                    "paths must never match"
                )

            if not DEMO_ORDER_PATH.startswith(
                "/capi/v3/sim/"
            ):
                raise RuntimeError(
                    "Invalid demo-order path"
                )

            # ================================================
            # BUILD DEMO ORDER
            # ================================================

            stage = (
                "demo order construction"
            )

            demo_payload = (
                create_demo_order_payload(
                    demo_quantity
                )
            )

            print(
                "R18 DEMO ORDER PAYLOAD:"
            )

            print(
                compact_json(
                    demo_payload
                )
            )

            # ================================================
            # DEMO ORDER TRANSMISSION
            # ================================================

            stage = (
                "demo order transmission"
            )

            if not DEMO_ORDER_ENABLED:
                raise RuntimeError(
                    "DEMO_ORDER_ENABLED "
                    "is FALSE"
                )

            demo_result = (
                await demo_post(
                    session=session,
                    path=DEMO_ORDER_PATH,
                    payload=demo_payload,
                )
            )

            # ================================================
            # VERIFY REAL POST NEVER CALLED
            # ================================================

            stage = (
                "post-transmission safety"
            )

            if real_post_called:
                raise RuntimeError(
                    "CRITICAL: real-order "
                    "POST flag was triggered"
                )

            # ================================================
            # SUCCESS REPORT
            # ================================================

            report = build_success_report(
                api_symbol_allowed=(
                    api_symbol_allowed
                ),
                mark_price=(
                    mark_price
                ),
                demo_balance=(
                    demo_balance
                ),
                min_order=(
                    min_order
                ),
                qty_precision=(
                    qty_precision
                ),
                weex_min_leverage=(
                    weex_min_leverage
                ),
                weex_max_leverage=(
                    weex_max_leverage
                ),
                demo_margin=(
                    demo_margin
                ),
                demo_notional=(
                    demo_notional
                ),
                demo_quantity=(
                    demo_quantity
                ),
                total_exposure=(
                    total_exposure
                ),
                open_real_positions=(
                    open_real_positions
                ),
                demo_result=(
                    demo_result
                ),
            )

            print()
            print(
                report
            )
            print()
            print(
                "=" * 60
            )

            await send_telegram(
                session,
                report,
            )

        except Exception as exc:

            report = (
                build_error_report(
                    stage,
                    exc,
                )
            )

            print()
            print(
                report
            )
            print()

            await send_telegram(
                session,
                report,
            )


# ============================================================
# APPLICATION MAIN
# ============================================================

async def main():

    server = await start_health_server()

    try:
        await run_r18()

        print(
            "=" * 60
        )

        print(
            f"{MODULE_NAME} "
            "DIAGNOSTIC RUN COMPLETE"
        )

        print(
            "HEALTH SERVER REMAINS ACTIVE"
        )

        print(
            "=" * 60
        )

        await server.serve_forever()

    finally:
        server.close()

        await server.wait_closed()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        print(
            f"{MODULE_NAME} STOPPED"
        )
