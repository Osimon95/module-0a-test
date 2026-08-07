import asyncio
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE 0E-2
# BTCUSDT 1-MINUTE EMA CROSS ENGINE
# EMA19 / EMA50 / EMA200
# ============================================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"
REST_URL = "https://api-contract.weex.com"

SYMBOL = "BTCUSDT"
INTERVAL = "1m"

SUBSCRIPTION_CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"

EMA_FAST = 19
EMA_MEDIUM = 50
EMA_SLOW = 200

HISTORY_LIMIT = 250

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# TELEGRAM CONFIGURATION
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


async def send_telegram(
    bot: Bot,
    message: str,
) -> None:

    if not telegram_is_configured():
        print(
            "TELEGRAM WARNING: Token or chat ID missing.",
            flush=True,
        )
        return

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print(
            "TELEGRAM MESSAGE SENT",
            flush=True,
        )

    except Exception as error:
        print(
            f"TELEGRAM ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )


# ============================================================
# DECIMAL CONVERSION
# ============================================================

def to_decimal(
    value: Any,
) -> Optional[Decimal]:

    try:
        if value is None:
            return None

        result = Decimal(str(value))

        if result <= 0:
            return None

        return result

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return None


# ============================================================
# EMA CALCULATION
# ============================================================

def calculate_ema(
    prices: list[Decimal],
    period: int,
) -> Optional[Decimal]:

    if len(prices) < period:
        return None

    multiplier = Decimal("2") / Decimal(period + 1)

    initial_prices = prices[:period]

    ema = (
        sum(initial_prices)
        / Decimal(period)
    )

    for price in prices[period:]:
        ema = (
            price * multiplier
            + ema * (
                Decimal("1")
                - multiplier
            )
        )

    return ema


# ============================================================
# EMA STRUCTURE
# ============================================================

def get_structure(
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> str:

    if ema19 > ema50 > ema200:
        return (
            "🟢 STRONG BULLISH "
            "EMA19 > EMA50 > EMA200"
        )

    if ema19 < ema50 < ema200:
        return (
            "🔴 STRONG BEARISH "
            "EMA19 < EMA50 < EMA200"
        )

    if ema19 > ema50:
        return (
            "🟡 EARLY / MIXED BULLISH"
        )

    if ema19 < ema50:
        return (
            "🟠 EARLY / MIXED BEARISH"
        )

    return "⚪ NEUTRAL"


# ============================================================
# EMA GAP
# ============================================================

def percentage_gap(
    fast: Decimal,
    slow: Decimal,
) -> Decimal:

    if slow == 0:
        return Decimal("0")

    return (
        (fast - slow)
        / slow
    ) * Decimal("100")


# ============================================================
# CROSS DETECTION
# ============================================================

async def detect_crosses(
    bot: Bot,
    previous_ema19: Decimal,
    previous_ema50: Decimal,
    previous_ema200: Decimal,
    current_ema19: Decimal,
    current_ema50: Decimal,
    current_ema200: Decimal,
    close_price: Decimal,
) -> None:

    # --------------------------------------------------------
    # EMA19 CROSS ABOVE EMA50
    # --------------------------------------------------------

    if (
        previous_ema19 <= previous_ema50
        and current_ema19 > current_ema50
    ):

        print(
            "CROSS DETECTED: "
            "EMA19 ABOVE EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            "🟢 EARLY BULLISH CROSS\n\n"
            "BTCUSDT 1m\n"
            "EMA19 crossed ABOVE EMA50\n\n"
            f"Price: {close_price}\n"
            f"EMA19: {current_ema19:.2f}\n"
            f"EMA50: {current_ema50:.2f}",
        )

    # --------------------------------------------------------
    # EMA19 CROSS BELOW EMA50
    # --------------------------------------------------------

    elif (
        previous_ema19 >= previous_ema50
        and current_ema19 < current_ema50
    ):

        print(
            "CROSS DETECTED: "
            "EMA19 BELOW EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            "🔴 EARLY BEARISH CROSS\n\n"
            "BTCUSDT 1m\n"
            "EMA19 crossed BELOW EMA50\n\n"
            f"Price: {close_price}\n"
            f"EMA19: {current_ema19:.2f}\n"
            f"EMA50: {current_ema50:.2f}",
        )

    # --------------------------------------------------------
    # EMA50 CROSS ABOVE EMA200
    # --------------------------------------------------------

    if (
        previous_ema50 <= previous_ema200
        and current_ema50 > current_ema200
    ):

        print(
            "CROSS DETECTED: "
            "EMA50 ABOVE EMA200",
            flush=True,
        )

        await send_telegram(
            bot,
            "🔥 GOLDEN CROSS\n\n"
            "BTCUSDT 1m\n"
            "EMA50 crossed ABOVE EMA200\n\n"
            f"Price: {close_price}\n"
            f"EMA50: {current_ema50:.2f}\n"
            f"EMA200: {current_ema200:.2f}",
        )

    # --------------------------------------------------------
    # EMA50 CROSS BELOW EMA200
    # --------------------------------------------------------

    elif (
        previous_ema50 >= previous_ema200
        and current_ema50 < current_ema200
    ):

        print(
            "CROSS DETECTED: "
            "EMA50 BELOW EMA200",
            flush=True,
        )

        await send_telegram(
            bot,
            "⚠️ DEATH CROSS\n\n"
            "BTCUSDT 1m\n"
            "EMA50 crossed BELOW EMA200\n\n"
            f"Price: {close_price}\n"
            f"EMA50: {current_ema50:.2f}\n"
            f"EMA200: {current_ema200:.2f}",
        )


# ============================================================
# HISTORICAL CANDLES
# ============================================================

async def load_historical_candles() -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    url = (
        f"{REST_URL}/capi/v2/market/candles"
        f"?symbol={SYMBOL}"
        f"&interval={INTERVAL}"
        f"&limit={HISTORY_LIMIT}"
    )

    prices: list[Decimal] = []

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                timeout=15,
            ) as response:

                data = await response.json()

        candles = data

        if isinstance(data, dict):
            candles = (
                data.get("data")
                or data.get("result")
                or []
            )

        if not isinstance(candles, list):
            raise ValueError(
                "Unexpected historical candle format"
            )

        for candle in candles:

            close_price = None

            if isinstance(candle, list):

                if len(candle) >= 5:
                    close_price = to_decimal(
                        candle[4]
                    )

            elif isinstance(candle, dict):

                close_price = to_decimal(
                    candle.get("close")
                    or candle.get("c")
                )

            if close_price is not None:
                prices.append(close_price)

        if len(prices) > HISTORY_LIMIT:
            prices = prices[-HISTORY_LIMIT:]

        print(
            f"HISTORICAL CANDLES LOADED: "
            f"{len(prices)}",
            flush=True,
        )

        if prices:
            print(
                f"LATEST CLOSED PRICE: "
                f"{prices[-1]}",
                flush=True,
            )

        return prices

    except Exception as error:

        print(
            f"HISTORICAL DATA ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )

        return []


# ============================================================
# LIVE CANDLE EXTRACTION
# ============================================================

def extract_live_candle(
    message: Any,
):

    if not isinstance(message, dict):
        return None

    data = message.get("data")

    if data is None:
        return None

    if isinstance(data, list):

        if len(data) == 0:
            return None

        if isinstance(data[0], dict):
            data = data[0]

        elif isinstance(data[0], list):
            data = data[0]

    if not isinstance(data, dict):
        return None

    close_price = to_decimal(
        data.get("close")
        or data.get("c")
        or data.get("last")
        or data.get("lastPrice")
    )

    timestamp = (
        data.get("timestamp")
        or data.get("ts")
        or data.get("time")
        or data.get("t")
    )

    if close_price is None:
        return None

    return timestamp, close_price


# ============================================================
# PROCESS CLOSED CANDLE
# ============================================================

async def process_closed_candle(
    bot: Bot,
    prices: list[Decimal],
    close_price: Decimal,
) -> None:

    # Calculate PREVIOUS EMA state before adding
    # the newly closed candle.

    previous_ema19 = calculate_ema(
        prices,
        EMA_FAST,
    )

    previous_ema50 = calculate_ema(
        prices,
        EMA_MEDIUM,
    )

    previous_ema200 = calculate_ema(
        prices,
        EMA_SLOW,
    )

    # Add new closed candle.

    prices.append(close_price)

    # Keep enough history while preventing
    # unlimited memory growth.

    if len(prices) > HISTORY_LIMIT:
        prices.pop(0)

    # Calculate CURRENT EMA state.

    current_ema19 = calculate_ema(
        prices,
        EMA_FAST,
    )

    current_ema50 = calculate_ema(
        prices,
        EMA_MEDIUM,
    )

    current_ema200 = calculate_ema(
        prices,
        EMA_SLOW,
    )

    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E-2 - CLOSED 1m CANDLE",
        flush=True,
    )

    print(
        f"BTCUSDT CLOSE: {close_price}",
        flush=True,
    )

    print(
        f"CANDLES STORED: {len(prices)}",
        flush=True,
    )

    if (
        current_ema19 is None
        or current_ema50 is None
        or current_ema200 is None
    ):

        print(
            "WAITING FOR ENOUGH EMA DATA",
            flush=True,
        )

        return

    print(
        f"EMA19: {current_ema19:.2f}",
        flush=True,
    )

    print(
        f"EMA50: {current_ema50:.2f}",
        flush=True,
    )

    print(
        f"EMA200: {current_ema200:.2f}",
        flush=True,
    )

    structure = get_structure(
        current_ema19,
        current_ema50,
        current_ema200,
    )

    print(
        f"STRUCTURE: {structure}",
        flush=True,
    )

    gap_19_50 = percentage_gap(
        current_ema19,
        current_ema50,
    )

    gap_50_200 = percentage_gap(
        current_ema50,
        current_ema200,
    )

    print(
        f"EMA19 ↔ EMA50 GAP: "
        f"{gap_19_50:.4f}%",
        flush=True,
    )

    print(
        f"EMA50 ↔ EMA200 GAP: "
        f"{gap_50_200:.4f}%",
        flush=True,
    )

    # Cross detection requires both previous
    # and current EMA values.

    if (
        previous_ema19 is not None
        and previous_ema50 is not None
        and previous_ema200 is not None
    ):

        await detect_crosses(
            bot,
            previous_ema19,
            previous_ema50,
            previous_ema200,
            current_ema19,
            current_ema50,
            current_ema200,
            close_price,
        )


# ============================================================
# WEBSOCKET
# ============================================================

async def run_websocket(
    bot: Bot,
    prices: list[Decimal],
) -> None:

    reconnect_delay = RECONNECT_DELAY_SECONDS

    current_candle_timestamp = None
    current_candle_close = None

    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                    "WEEX-EMA-Bot/0E-2"
                },
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
            ) as websocket:

                print(
                    "CONNECTED TO WEEX",
                    flush=True,
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
                    f"SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}",
                    flush=True,
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                async for raw_message in websocket:

                    try:

                        message = json.loads(
                            raw_message
                        )

                    except json.JSONDecodeError:
                        continue

                    # Subscription acknowledgement

                    if (
                        isinstance(message, dict)
                        and message.get("id") == 1
                    ):

                        print(
                            "SUBSCRIPTION CONFIRMED",
                            flush=True,
                        )

                        continue

                    # WEEX application ping

                    if (
                        isinstance(message, dict)
                        and "ping" in message
                    ):

                        pong_message = {
                            "pong": message["ping"]
                        }

                        await websocket.send(
                            json.dumps(
                                pong_message
                            )
                        )

                        print(
                            "APPLICATION PONG SENT",
                            flush=True,
                        )

                        continue

                    candle = extract_live_candle(
                        message
                    )

                    if candle is None:
                        continue

                    (
                        candle_timestamp,
                        candle_close,
                    ) = candle

                    if current_candle_timestamp is None:

                        current_candle_timestamp = (
                            candle_timestamp
                        )

                        current_candle_close = (
                            candle_close
                        )

                        print(
                            "LIVE 1m CANDLE STARTED: "
                            f"{candle_close}",
                            flush=True,
                        )

                        continue

                    # Same candle still updating.

                    if (
                        candle_timestamp
                        == current_candle_timestamp
                    ):

                        current_candle_close = (
                            candle_close
                        )

                        continue

                    # Timestamp changed.
                    # Previous candle is now closed.

                    if current_candle_close is not None:

                        await process_closed_candle(
                            bot,
                            prices,
                            current_candle_close,
                        )

                    current_candle_timestamp = (
                        candle_timestamp
                    )

                    current_candle_close = (
                        candle_close
                    )

        except Exception as error:

            print(
                f"CONNECTION ERROR: "
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )

            print(
                f"RECONNECTING IN "
                f"{reconnect_delay} SECONDS",
                flush=True,
            )

            await asyncio.sleep(
                reconnect_delay
            )

            reconnect_delay = min(
                reconnect_delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E-2 STARTING",
        flush=True,
    )

    print(
        "BTCUSDT 1-MINUTE EMA CROSS ENGINE",
        flush=True,
    )

    print(
        "EMA19 / EMA50 / EMA200",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )

    if telegram_is_configured():
        print(
            "TELEGRAM CONFIG: READY",
            flush=True,
        )
    else:
        print(
            "TELEGRAM CONFIG: MISSING",
            flush=True,
        )

    prices = await load_historical_candles()

    if len(prices) < EMA_SLOW:

        print(
            "ERROR: NOT ENOUGH HISTORICAL "
            "CANDLES FOR EMA200",
            flush=True,
        )

        return

    ema19 = calculate_ema(
        prices,
        EMA_FAST,
    )

    ema50 = calculate_ema(
        prices,
        EMA_MEDIUM,
    )

    ema200 = calculate_ema(
        prices,
        EMA_SLOW,
    )

    print(
        "INITIAL EMA ENGINE",
        flush=True,
    )

    print(
        f"EMA19: {ema19:.2f}",
        flush=True,
    )

    print(
        f"EMA50: {ema50:.2f}",
        flush=True,
    )

    print(
        f"EMA200: {ema200:.2f}",
        flush=True,
    )

    structure = get_structure(
        ema19,
        ema50,
        ema200,
    )

    print(
        f"STRUCTURE: {structure}",
        flush=True,
    )

    print(
        "EMA CROSS ENGINE READY",
        flush=True,
    )

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    await send_telegram(
        bot,
        "✅ MODULE 0E-2 CONNECTED\n\n"
        "BTCUSDT 1-minute EMA cross engine\n\n"
        "EMA19 ↔ EMA50 ✅\n"
        "EMA50 ↔ EMA200 ✅\n\n"
        "Cross alerts armed.",
    )

    await run_websocket(
        bot,
        prices,
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
