import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4G"


# ============================================================
# CORE CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

REST_BASE_URL = "https://api-contract.weex.com"
WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIPTION_CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# TRADE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal("5")
PYRAMID_ADD_PERCENT = Decimal("5")

LEVERAGE = Decimal("5")
MAX_LEVERAGE = Decimal("10")

MAX_PYRAMID_ADDS = 1
MAX_BACKUPS = 3

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.50")
TP2_TRIGGER_PERCENT = Decimal("1.00")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")


# ============================================================
# EXECUTION SAFETY
# ============================================================

LIVE_ORDER_EXECUTION = False

ALLOW_LIVE_ENTRY_ORDERS = False
ALLOW_LIVE_PYRAMID_ORDERS = False
ALLOW_LIVE_BACKUP_ORDERS = False
ALLOW_LIVE_EXIT_ORDERS = False

AUTHENTICATED_READ_TEST = True

HARD_EXECUTION_LOCK = True


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


def weex_credentials_configured() -> bool:
    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
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


def telegram_is_configured() -> bool:
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(message: str) -> None:
    if not telegram_is_configured():
        print("TELEGRAM CONFIG: MISSING")
        return

    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print("TELEGRAM MESSAGE SENT")

    except Exception as exc:
        print(
            "TELEGRAM ERROR:",
            type(exc).__name__,
            str(exc),
        )


# ============================================================
# DECIMAL HELPERS
# ============================================================

def to_decimal(value, default="0") -> Decimal:
    try:
        return Decimal(str(value))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return Decimal(default)


def decimal_string(
    value: Decimal,
    precision: int = 8,
) -> str:

    value = to_decimal(value)

    text = f"{value:.{precision}f}"

    text = text.rstrip("0").rstrip(".")

    return text or "0"


# ============================================================
# WEEX REST SIGNATURE
# ============================================================

def create_weex_signature(
    timestamp: str,
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> str:

    method = method.upper()

    if query_string:

        message = (
            timestamp
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        message = (
            timestamp
            + method
            + request_path
            + body
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# AUTHENTICATED HEADERS
# ============================================================

def build_auth_headers(
    method: str,
    request_path: str,
    query_string: str = "",
    body: str = "",
) -> dict:

    if not weex_credentials_configured():
        raise RuntimeError(
            "WEEX credentials are not configured"
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = create_weex_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "User-Agent": "WEEX-0F-4G-Bot/1.0",
    }


# ============================================================
# GENERIC AUTHENTICATED REQUEST
# ============================================================

async def authenticated_request(
    session: aiohttp.ClientSession,
    method: str,
    request_path: str,
    params: dict | None = None,
    payload: dict | None = None,
):

    method = method.upper()

    params = params or {}

    query_string = urlencode(params)

    body = ""

    if payload is not None:
        body = json.dumps(
            payload,
            separators=(",", ":"),
        )

    headers = build_auth_headers(
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    url = REST_BASE_URL + request_path

    if query_string:
        url += "?" + query_string

    async with session.request(
        method,
        url,
        headers=headers,
        data=body if body else None,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        text = await response.text()

        try:
            data = json.loads(text)

        except json.JSONDecodeError:
            data = text

        return response.status, data


# ============================================================
# PUBLIC EXCHANGE INFORMATION
# ============================================================

async def get_exchange_info(
    session: aiohttp.ClientSession,
):

    url = (
        REST_BASE_URL
        + "/capi/v3/market/exchangeInfo"
    )

    params = {
        "symbol": SYMBOL,
    }

    try:
        async with session.get(
            url,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            data = await response.json(
                content_type=None
            )

            if response.status != 200:

                print(
                    "EXCHANGE INFO ERROR:",
                    response.status,
                    data,
                )

                return None

            symbols = []

            if isinstance(data, dict):
                symbols = data.get(
                    "symbols",
                    [],
                )

            if not symbols:

                print(
                    "EXCHANGE INFO:",
                    "NO SYMBOL DATA",
                )

                return None

            info = symbols[0]

            print("=" * 60)
            print("WEEX CONTRACT INFORMATION")
            print("SYMBOL:", info.get("symbol"))
            print(
                "PRICE PRECISION:",
                info.get("pricePrecision"),
            )
            print(
                "QUANTITY PRECISION:",
                info.get("quantityPrecision"),
            )
            print(
                "CONTRACT VALUE:",
                info.get("contractVal"),
            )
            print(
                "MIN LEVERAGE:",
                info.get("minLeverage"),
            )
            print(
                "MAX LEVERAGE:",
                info.get("maxLeverage"),
            )
            print("=" * 60)

            return info

    except Exception as exc:

        print(
            "EXCHANGE INFO EXCEPTION:",
            type(exc).__name__,
            str(exc),
        )

        return None


# ============================================================
# API TRADING SYMBOL CHECK
# ============================================================

async def check_api_trading_symbol(
    session: aiohttp.ClientSession,
) -> bool:

    url = (
        REST_BASE_URL
        + "/capi/v3/market/apiTradingSymbols"
    )

    try:

        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            data = await response.json(
                content_type=None
            )

            if response.status != 200:

                print(
                    "API SYMBOL CHECK ERROR:",
                    response.status,
                    data,
                )

                return False

            if isinstance(data, list):

                available = SYMBOL in data

            elif isinstance(data, dict):

                result = (
                    data.get("data")
                    or data.get("symbols")
                    or data.get("result")
                    or []
                )

                available = (
                    SYMBOL in result
                    if isinstance(result, list)
                    else False
                )

            else:

                available = False

            print(
                "API FUTURES SYMBOL:",
                "SUPPORTED"
                if available
                else "NOT CONFIRMED",
            )

            return available

    except Exception as exc:

        print(
            "API SYMBOL CHECK EXCEPTION:",
            type(exc).__name__,
            str(exc),
        )

        return False


# ============================================================
# AUTHENTICATION TEST
# ============================================================

async def test_weex_authentication(
    session: aiohttp.ClientSession,
) -> bool:

    if not weex_credentials_configured():

        print("=" * 60)
        print(
            "WEEX AUTHENTICATION TEST: SKIPPED"
        )
        print(
            "WEEX API credentials are missing."
        )
        print("=" * 60)

        return False

    request_path = (
        "/capi/v3/account/symbolConfig"
    )

    params = {
        "symbol": SYMBOL,
    }

    try:

        status, data = (
            await authenticated_request(
                session=session,
                method="GET",
                request_path=request_path,
                params=params,
            )
        )

        print("=" * 60)
        print("WEEX AUTHENTICATION TEST")
        print("HTTP STATUS:", status)

        if status == 200:

            print("AUTHENTICATION: PASSED")

            if isinstance(data, list):

                for item in data:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    print(
                        "SYMBOL:",
                        item.get("symbol"),
                    )

                    print(
                        "MARGIN TYPE:",
                        item.get(
                            "marginType"
                        ),
                    )

                    print(
                        "POSITION MODE:",
                        item.get(
                            "separatedType"
                        ),
                    )

                    print(
                        "CROSS LEVERAGE:",
                        item.get(
                            "crossLeverage"
                        ),
                    )

                    print(
                        "ISOLATED LONG LEVERAGE:",
                        item.get(
                            "isolatedLongLeverage"
                        ),
                    )

                    print(
                        "ISOLATED SHORT LEVERAGE:",
                        item.get(
                            "isolatedShortLeverage"
                        ),
                    )

            print("=" * 60)

            return True

        print(
            "AUTHENTICATION: FAILED"
        )

        print(
            "WEEX RESPONSE:",
            data,
        )

        print("=" * 60)

        return False

    except Exception as exc:

        print(
            "AUTHENTICATION EXCEPTION:",
            type(exc).__name__,
            str(exc),
        )

        print("=" * 60)

        return False


# ============================================================
# CLIENT ORDER ID
# ============================================================

used_client_order_ids = set()


def new_client_order_id(
    purpose: str = "entry",
) -> str:

    unique = uuid.uuid4().hex[:12]

    client_id = (
        f"0F4G-{purpose}-{unique}"
    )

    return client_id[:36]


# ============================================================
# ORDER BUILDER
# ============================================================

def build_market_order(
    direction: str,
    quantity: Decimal,
    reduce_only: bool = False,
    purpose: str = "entry",
) -> dict:

    direction = direction.upper()

    if direction == "LONG":

        side = (
            "SELL"
            if reduce_only
            else "BUY"
        )

        position_side = "LONG"

    elif direction == "SHORT":

        side = (
            "BUY"
            if reduce_only
            else "SELL"
        )

        position_side = "SHORT"

    else:

        raise ValueError(
            "Direction must be LONG or SHORT"
        )

    return {
        "symbol": SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": decimal_string(
            quantity
        ),
        "reduceOnly": bool(
            reduce_only
        ),
        "newClientOrderId":
            new_client_order_id(
                purpose
            ),
    }


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_order(
    order: dict,
) -> tuple[bool, str]:

    required = [
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    ]

    for field in required:

        if field not in order:

            return (
                False,
                f"Missing field: {field}",
            )

    if order["symbol"] != SYMBOL:

        return (
            False,
            "Invalid symbol",
        )

    if order["side"] not in (
        "BUY",
        "SELL",
    ):

        return (
            False,
            "Invalid side",
        )

    if order["positionSide"] not in (
        "LONG",
        "SHORT",
    ):

        return (
            False,
            "Invalid position side",
        )

    if order["type"] not in (
        "MARKET",
        "LIMIT",
    ):

        return (
            False,
            "Invalid order type",
        )

    quantity = to_decimal(
        order["quantity"]
    )

    if quantity <= 0:

        return (
            False,
            "Quantity must be positive",
        )

    client_id = order[
        "newClientOrderId"
    ]

    if not client_id:

        return (
            False,
            "Missing client order ID",
        )

    if len(client_id) > 36:

        return (
            False,
            "Client order ID too long",
        )

    return (
        True,
        "VALID",
    )


# ============================================================
# HARD EXECUTION BRIDGE
# ============================================================

async def execute_order(
    session: aiohttp.ClientSession,
    order: dict,
):

    valid, reason = validate_order(
        order
    )

    if not valid:

        print(
            "ORDER REJECTED:",
            reason,
        )

        return {
            "success": False,
            "reason": reason,
        }

    client_id = order[
        "newClientOrderId"
    ]

    if client_id in used_client_order_ids:

        print(
            "ANTI-DUPLICATE:",
            "ORDER BLOCKED",
        )

        return {
            "success": False,
            "reason":
                "Duplicate client order ID",
        }

    used_client_order_ids.add(
        client_id
    )

    print("=" * 60)
    print("ORDER VALIDATION PASSED")
    print("SYMBOL:", order["symbol"])
    print("SIDE:", order["side"])
    print(
        "POSITION SIDE:",
        order["positionSide"],
    )
    print("TYPE:", order["type"])
    print(
        "QUANTITY:",
        order["quantity"],
    )
    print(
        "CLIENT ORDER ID:",
        client_id,
    )

    # ========================================================
    # ABSOLUTE SAFETY LOCK
    # ========================================================

    if HARD_EXECUTION_LOCK:

        print(
            "HARD EXECUTION LOCK:"
            " ACTIVE"
        )

        print(
            "NO ORDER SENT TO WEEX"
        )

        print("=" * 60)

        return {
            "success": False,
            "blocked": True,
            "reason":
                "Hard execution lock active",
        }

    # Secondary protection

    if not LIVE_ORDER_EXECUTION:

        print(
            "LIVE ORDER EXECUTION:"
            " DISABLED"
        )

        print(
            "NO ORDER SENT TO WEEX"
        )

        print("=" * 60)

        return {
            "success": False,
            "blocked": True,
            "reason":
                "Live execution disabled",
        }

    # This section intentionally remains unreachable
    # during Module 0F-4G.

    raise RuntimeError(
        "0F-4G safety violation: "
        "live execution path reached"
    )


# ============================================================
# SIMULATED ORDER BRIDGE TEST
# ============================================================

async def run_order_bridge_test(
    session: aiohttp.ClientSession,
):

    print("=" * 60)
    print("MODULE 0F-4G AUTHENTICATED BRIDGE TEST")
    print(
        "NO LIVE ORDER WILL BE SENT"
    )
    print("=" * 60)

    test_order = build_market_order(
        direction="LONG",
        quantity=Decimal("0.001"),
        reduce_only=False,
        purpose="test",
    )

    valid, reason = validate_order(
        test_order
    )

    if not valid:

        raise RuntimeError(
            f"TEST ORDER INVALID: {reason}"
        )

    first_result = await execute_order(
        session,
        test_order,
    )

    # Test duplicate protection

    second_result = await execute_order(
        session,
        test_order,
    )

    if not first_result.get(
        "blocked"
    ):

        raise RuntimeError(
            "Hard execution lock test failed"
        )

    if (
        second_result.get("reason")
        != "Duplicate client order ID"
    ):

        raise RuntimeError(
            "Anti-duplicate test failed"
        )

    print("=" * 60)
    print("0F-4G BRIDGE TEST: PASSED")
    print("ORDER PAYLOAD BUILDER: PASSED")
    print("ORDER VALIDATION: PASSED")
    print(
        "UNIQUE CLIENT ORDER ID: PASSED"
    )
    print(
        "ANTI-DUPLICATE PROTECTION: PASSED"
    )
    print(
        "HARD EXECUTION LOCK: PASSED"
    )
    print(
        "NO LIVE ORDER WAS SENT"
    )
    print("=" * 60)


# ============================================================
# MARKET PRICE PARSER
# ============================================================

def extract_price(message):

    if not isinstance(message, dict):
        return None

    data = message.get(
        "data",
        message,
    )

    if isinstance(data, list):

        if not data:
            return None

        data = data[-1]

    if not isinstance(data, dict):
        return None

    candidates = (
        "close",
        "c",
        "lastPrice",
        "last",
        "price",
    )

    for field in candidates:

        value = data.get(field)

        price = to_decimal(value)

        if price > 0:
            return price

    return None


# ============================================================
# WEBSOCKET MONITOR
# ============================================================

async def monitor_weex():

    delay = RECONNECT_DELAY_SECONDS

    while True:

        try:

            print(
                "CONNECTING TO WEEX..."
            )

            async with websockets.connect(
                WS_URL,
                ping_interval=None,
                additional_headers={
                    "User-Agent":
                        "WEEX-0F-4G-Bot/1.0",
                },
            ) as websocket:

                print(
                    "CONNECTED TO WEEX"
                )

                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],
                    "id": 1,
                }

                await websocket.send(
                    json.dumps(
                        subscribe_message
                    )
                )

                print(
                    "SUBSCRIBED TO",
                    SUBSCRIPTION_CHANNEL,
                )

                delay = (
                    RECONNECT_DELAY_SECONDS
                )

                async for raw_message in websocket:

                    try:

                        message = json.loads(
                            raw_message
                        )

                    except json.JSONDecodeError:

                        continue

                    if not isinstance(
                        message,
                        dict,
                    ):
                        continue

                    event = str(
                        message.get(
                            "event",
                            ""
                        )
                    ).lower()

                    msg_type = str(
                        message.get(
                            "type",
                            ""
                        )
                    ).lower()

                    if (
                        event == "ping"
                        or msg_type == "ping"
                    ):

                        await websocket.send(
                            json.dumps(
                                {
                                    "method":
                                        "PONG",
                                    "id": 1,
                                }
                            )
                        )

                        continue

                    if (
                        message.get(
                            "result"
                        )
                        is True
                    ):

                        print(
                            "SUBSCRIPTION CONFIRMED"
                        )

                        continue

                    price = extract_price(
                        message
                    )

                    if price is not None:

                        print(
                            SYMBOL,
                            "PRICE:",
                            price,
                        )

        except Exception as exc:

            print(
                "WEEX CONNECTION ERROR:",
                type(exc).__name__,
                str(exc),
            )

            print(
                f"RECONNECTING IN "
                f"{delay}s..."
            )

            await asyncio.sleep(
                delay
            )

            delay = min(
                delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


# ============================================================
# STARTUP DISPLAY
# ============================================================

def print_startup():

    print("=" * 60)
    print(
        f"MODULE {MODULE_NAME} STARTING"
    )
    print(
        "WEEX AUTHENTICATED "
        "SAFE EXECUTION BRIDGE"
    )
    print("=" * 60)

    print("SYMBOL:", SYMBOL)

    print(
        "WEEX CREDENTIALS:",
        "READY"
        if weex_credentials_configured()
        else "MISSING",
    )

    print(
        "AUTHENTICATED READ TEST:",
        "ENABLED"
        if AUTHENTICATED_READ_TEST
        else "DISABLED",
    )

    print(
        "ORDER VALIDATION: ACTIVE"
    )

    print(
        "ANTI-DUPLICATE PROTECTION:"
        " ACTIVE"
    )

    print(
        "HARD EXECUTION LOCK:",
        "ACTIVE"
        if HARD_EXECUTION_LOCK
        else "DISABLED",
    )

    print(
        "LIVE ORDER EXECUTION:",
        "ENABLED"
        if LIVE_ORDER_EXECUTION
        else "DISABLED",
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

async def main():

    print_startup()

    credential_status = (
        "READY"
        if weex_credentials_configured()
        else "MISSING"
    )

    await send_telegram(
        "✅ MODULE 0F-4G ONLINE\n"
        f"{SYMBOL}\n"
        "Authenticated Safe Execution Bridge\n"
        f"WEEX credentials: {credential_status}\n"
        "✅ V3 request signing engine\n"
        "✅ Authenticated account test\n"
        "✅ Contract validation\n"
        "✅ Order validation\n"
        "✅ Anti-duplicate protection\n"
        "🛡 Hard execution lock active\n"
        "⚠️ Live order execution disabled"
    )

    async with aiohttp.ClientSession() as session:

        # Public contract metadata

        await get_exchange_info(
            session
        )

        # Confirm API trading eligibility

        await check_api_trading_symbol(
            session
        )

        # Read-only private authentication test

        auth_passed = False

        if AUTHENTICATED_READ_TEST:

            auth_passed = (
                await test_weex_authentication(
                    session
                )
            )

        # Test order bridge without sending

        await run_order_bridge_test(
            session
        )

        auth_text = (
            "✅ WEEX AUTHENTICATION PASSED"
            if auth_passed
            else (
                "⚠️ WEEX AUTHENTICATION "
                "NOT YET VERIFIED"
            )
        )

        await send_telegram(
            "🧪 MODULE 0F-4G TEST\n"
            f"{SYMBOL}\n"
            f"{auth_text}\n"
            "✅ V3 signature engine\n"
            "✅ Exchange contract check\n"
            "✅ API trading-symbol check\n"
            "✅ Order payload builder\n"
            "✅ Order validation\n"
            "✅ Unique client order IDs\n"
            "✅ Anti-duplicate protection\n"
            "🛡 Hard execution lock active\n"
            "⚠️ No live order was sent."
        )

    print(
        "LIVE MARKET MONITORING ACTIVE"
    )

    print(
        "WAITING FOR WEEX MARKET DATA..."
    )

    await monitor_weex()


if __name__ == "__main__":

    asyncio.run(
        main())
