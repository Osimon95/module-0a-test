import asyncio
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE 0E-3
# BTCUSDT 1-MINUTE EMA CROSSOVER ENGINE
#
# EMA19  = FAST MOMENTUM
# EMA50  = MEDIUM TREND
# EMA200 = MAJOR TREND
#
# Detects:
# EMA19 / EMA50 bullish & bearish crosses
# EMA50 / EMA200 Golden Cross & Death Cross
# ============================================================


WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SYMBOL = "BTCUSDT"

SUBSCRIPTION_CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# TELEGRAM
# ============================================================

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

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    initial_prices = prices[:period]

    ema = (
        sum(initial_prices)
        / Decimal(period)
    )

    for price in prices[period:]:

        ema = (
            (price - ema)
            * multiplier
            + ema
        )

    return ema
# ============================================================
# EMA STRUCTURE
# ============================================================

def get_ema_structure(
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> str:

    if (
        ema19 > ema50
        and ema50 > ema200
    ):

        return (
            "🟢 STRONG BULLISH "
            "EMA19 > EMA50 > EMA200"
        )

    if (
        ema19 < ema50
        and ema50 < ema200
    ):

        return (
            "🔴 STRONG BEARISH "
            "EMA19 < EMA50 < EMA200"
        )

    if ema19 > ema50:

        return (
            "🟡 SHORT-TERM BULLISH / "
            "MIXED STRUCTURE"
        )

    if ema19 < ema50:

        return (
            "🟡 SHORT-TERM BEARISH / "
            "MIXED STRUCTURE"
        )

    return "⚪ NEUTRAL EMA STRUCTURE"


# ============================================================
# MODULE 0E-3
# EMA CROSS DETECTOR
# ============================================================

def detect_ema_crosses(
    previous_ema19: Decimal,
    previous_ema50: Decimal,
    previous_ema200: Decimal,
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> list[str]:

    events = []


    # --------------------------------------------------------
    # EMA19 CROSS ABOVE EMA50
    # --------------------------------------------------------

    if (
        previous_ema19 <= previous_ema50
        and ema19 > ema50
    ):

        events.append(
            "🟢 EMA19 BULLISH CROSS\n"
            "EMA19 crossed ABOVE EMA50"
        )


    # --------------------------------------------------------
    # EMA19 CROSS BELOW EMA50
    # --------------------------------------------------------

    if (
        previous_ema19 >= previous_ema50
        and ema19 < ema50
    ):

        events.append(
            "🔴 EMA19 BEARISH CROSS\n"
            "EMA19 crossed BELOW EMA50"
        )


    # --------------------------------------------------------
    # EMA50 CROSS ABOVE EMA200
    # GOLDEN CROSS
    # --------------------------------------------------------

    if (
        previous_ema50 <= previous_ema200
        and ema50 > ema200
    ):

        events.append(
            "🟢 GOLDEN CROSS\n"
            "EMA50 crossed ABOVE EMA200"
        )


    # --------------------------------------------------------
    # EMA50 CROSS BELOW EMA200
    # DEATH CROSS
    # --------------------------------------------------------

    if (
        previous_ema50 >= previous_ema200
        and ema50 < ema200
    ):

        events.append(
            "🔴 DEATH CROSS\n"
            "EMA50 crossed BELOW EMA200"
        )


    return events


# ============================================================
# HISTORICAL CANDLES
# ============================================================

async def load_historical_candles() -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    urls = [

        (
            "https://api-contract.weex.com"
            "/capi/v2/market/candles"
            f"?symbol={SYMBOL}"
            "&granularity=1m"
            "&limit=250"
        ),

        (
            "https://api-contract.weex.com"
            "/capi/v2/market/candles"
            f"?symbol={SYMBOL}"
            "&granularity=60"
            "&limit=250"
        ),
    ]


    headers = {
        "User-Agent": "WEEX-BTC-Bot/1.0"
    }


    async with aiohttp.ClientSession(
        headers=headers
    ) as session:

        for url in urls:

            try:

                async with session.get(
                    url,
                    timeout=15,
                ) as response:

                    print(
                        "HISTORICAL HTTP STATUS:",
                        response.status,
                        flush=True,
                    )

                    if response.status != 200:
                        continue

                    data = await response.json()

                    candles = extract_historical_prices(
                        data
                    )

                    if len(candles) >= 200:

                        print(
                            "HISTORICAL CANDLES LOADED:",
                            len(candles),
                            flush=True,
                        )

                        return candles

            except Exception as error:

                print(
                    "HISTORICAL ERROR:",
                    type(error).__name__,
                    error,
                    flush=True,
                )


    return []
# ============================================================
# HISTORICAL PRICE EXTRACTION
# ============================================================

def extract_historical_prices(
    data: Any,
) -> list[Decimal]:

    if isinstance(data, dict):

        for key in (
            "data",
            "result",
            "candles",
        ):

            if key in data:

                return extract_historical_prices(
                    data[key]
                )


    if not isinstance(data, list):
        return []


    prices = []


    for candle in data:

        close_price = None


        # Common candle format:
        #
        # [
        # timestamp,
        # open,
        # high,
        # low,
        # close,
        # volume
        # ]

        if isinstance(candle, list):

            if len(candle) >= 5:

                close_price = to_decimal(
                    candle[4]
                )


        elif isinstance(candle, dict):

            for key in (
                "close",
                "c",
                "closePrice",
            ):

                if key in candle:

                    close_price = to_decimal(
                        candle[key]
                    )

                    if close_price:
                        break


        if close_price:

            prices.append(
                close_price
            )


    # WEEX may return newest candle first.
    #
    # Reverse if necessary so the EMA engine always
    # processes candles oldest -> newest.

    if len(prices) >= 2:

        first_timestamp = None
        last_timestamp = None


        try:

            first_item = data[0]
            last_item = data[-1]

            if isinstance(first_item, list):
                first_timestamp = Decimal(
                    str(first_item[0])
                )

            if isinstance(last_item, list):
                last_timestamp = Decimal(
                    str(last_item[0])
                )

        except Exception:

            pass


        if (
            first_timestamp is not None
            and last_timestamp is not None
            and first_timestamp > last_timestamp
        ):

            prices.reverse()


    return prices


# ============================================================
# WEBSOCKET KLINE EXTRACTION
# ============================================================

def extract_kline(
    message: Any,
) -> Optional[tuple]:

    if not isinstance(message, dict):
        return None


    data = message.get("data")


    if data is None:
        return None


    items = (
        data
        if isinstance(data, list)
        else [data]
    )


    for item in items:

        # ----------------------------------------------------
        # DICTIONARY FORMAT
        # ----------------------------------------------------

        if isinstance(item, dict):

            close_price = None

            for key in (
                "close",
                "c",
                "closePrice",
                "lastPrice",
                "last",
                "price",
            ):

                if key in item:

                    close_price = to_decimal(
                        item[key]
                    )

                    if close_price:
                        break


            if close_price is None:
                continue


            timestamp = (
                item.get("timestamp")
                or item.get("ts")
                or item.get("time")
                or item.get("startTime")
                or item.get("t")
            )


            return (
                timestamp,
                close_price,
            )


        # ----------------------------------------------------
        # ARRAY FORMAT
        # ----------------------------------------------------

        if isinstance(item, list):

            if len(item) >= 5:

                timestamp = item[0]

                close_price = to_decimal(
                    item[4]
                )

                if close_price:

                    return (
                        timestamp,
                        close_price,
                    )


    return None


# ============================================================
# MAIN WEBSOCKET ENGINE
# ============================================================

async def run_websocket(
    bot: Bot,
    prices: list[Decimal],
) -> None:

    reconnect_delay = RECONNECT_DELAY_SECONDS

    current_candle_timestamp = None

    current_candle_price = None


    previous_ema19 = calculate_ema(
        prices,
        19,
    )

    previous_ema50 = calculate_ema(
        prices,
        50,
    )

    previous_ema200 = calculate_ema(
        prices,
        200,
    )


    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                    "WEEX-BTC-Bot/1.0"
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
                    "SUBSCRIBED TO",
                    SUBSCRIPTION_CHANNEL,
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


                    # ----------------------------------------
                    # WEEX APPLICATION PING
                    # ----------------------------------------

                    if isinstance(message, dict):

                        if (
                            message.get("method")
                            == "PING"
                        ):

                            pong = {
                                "method": "PONG"
                            }

                            await websocket.send(
                                json.dumps(pong)
                            )

                            print(
                                "APPLICATION PONG SENT",
                                flush=True,
                            )

                            continue


                    # ----------------------------------------
                    # SUBSCRIPTION CONFIRMATION
                    # ----------------------------------------

                    if isinstance(message, dict):

                        if (
                            message.get("id") == 1
                            or message.get("result")
                            is not None
                        ):

                            print(
                                "SUBSCRIPTION CONFIRMED",
                                flush=True,
                            )


                    kline = extract_kline(
                        message
                    )


                    if kline is None:
                        continue


                    candle_timestamp, price = kline
                   # ========================================
                    # FIRST LIVE CANDLE
                    # ========================================

                    if (
                        current_candle_timestamp
                        is None
                    ):

                        current_candle_timestamp = (
                            candle_timestamp
                        )

                        current_candle_price = price

                        print(
                            "LIVE 1m CANDLE STARTED:",
                            price,
                            flush=True,
                        )

                        continue


                    # ========================================
                    # SAME LIVE CANDLE
                    # ========================================

                    if (
                        candle_timestamp
                        == current_candle_timestamp
                    ):

                        current_candle_price = price

                        continue


                    # ========================================
                    # PREVIOUS 1-MINUTE CANDLE CLOSED
                    # ========================================

                    closed_price = (
                        current_candle_price
                    )


                    prices.append(
                        closed_price
                    )


                    # Keep enough history without allowing
                    # the list to grow forever.

                    if len(prices) > 500:

                        prices[:] = prices[-500:]


                    ema19 = calculate_ema(
                        prices,
                        19,
                    )

                    ema50 = calculate_ema(
                        prices,
                        50,
                    )

                    ema200 = calculate_ema(
                        prices,
                        200,
                    )


                    print(
                        "=" * 40,
                        flush=True,
                    )

                    print(
                        "MODULE 0E-3 - CLOSED 1m CANDLE",
                        flush=True,
                    )

                    print(
                        f"{SYMBOL} CLOSE:",
                        closed_price,
                        flush=True,
                    )

                    print(
                        "EMA19:",
                        (
                            round(ema19, 2)
                            if ema19
                            else "N/A"
                        ),
                        flush=True,
                    )

                    print(
                        "EMA50:",
                        (
                            round(ema50, 2)
                            if ema50
                            else "N/A"
                        ),
                        flush=True,
                    )

                    print(
                        "EMA200:",
                        (
                            round(ema200, 2)
                            if ema200
                            else "N/A"
                        ),
                        flush=True,
                    )


                    if (
                        ema19 is not None
                        and ema50 is not None
                        and ema200 is not None
                    ):

                        structure = get_ema_structure(
                            ema19,
                            ema50,
                            ema200,
                        )


                        print(
                            "STRUCTURE:",
                            structure,
                            flush=True,
                        )


                        # ====================================
                        # 0E-3 CROSSOVER DETECTION
                        # ====================================

                        if (
                            previous_ema19
                            is not None
                            and previous_ema50
                            is not None
                            and previous_ema200
                            is not None
                        ):

                            cross_events = (
                                detect_ema_crosses(
                                    previous_ema19,
                                    previous_ema50,
                                    previous_ema200,
                                    ema19,
                                    ema50,
                                    ema200,
                                )
                            )


                            for event in cross_events:

                                print(
                                    "=" * 40,
                                    flush=True,
                                )

                                print(
                                    "EMA CROSS EVENT",
                                    flush=True,
                                )

                                print(
                                    event,
                                    flush=True,
                                )


                                telegram_message = (
                                    f"{event}\n\n"
                                    f"{SYMBOL}\n"
                                    f"Price: "
                                    f"{closed_price}\n\n"
                                    f"EMA19: "
                                    f"{ema19:.2f}\n"
                                    f"EMA50: "
                                    f"{ema50:.2f}\n"
                                    f"EMA200: "
                                    f"{ema200:.2f}\n\n"
                                    f"{structure}"
                                )


                                await send_telegram(
                                    bot,
                                    telegram_message,
                                )


                        # Store the new EMA state.
                        #
                        # This becomes the "previous"
                        # candle during the next close.

                        previous_ema19 = ema19
                        previous_ema50 = ema50
                        previous_ema200 = ema200


                    # ========================================
                    # START NEW LIVE CANDLE
                    # ========================================

                    current_candle_timestamp = (
                        candle_timestamp
                    )

                    current_candle_price = price


                    print(
                        "NEW LIVE 1m CANDLE:",
                        price,
                        flush=True,
                    )


        except Exception as error:

            print(
                "CONNECTION ERROR:",
                f"{type(error).__name__}:",
                error,
                flush=True,
            )

            print(
                "RECONNECTING IN",
                reconnect_delay,
                "SECONDS",
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
# APPLICATION STARTUP
# ============================================================

async def main() -> None:

    print(
        "=" * 40,
        flush=True,
    )

    print(
        "MODULE 0E-3 STARTING",
        flush=True,
    )

    print(
        "BTCUSDT 1-MINUTE EMA CROSSOVER ENGINE",
        flush=True,
    )

    print(
        "EMA19 / EMA50 / EMA200",
        flush=True,
    )

    print(
        "=" * 40,
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


    if len(prices) < 200:

        print(
            "ERROR: NOT ENOUGH HISTORICAL "
            "CANDLES FOR EMA200",
            flush=True,
        )

        return


    print(
        "LATEST CLOSED PRICE:",
        prices[-1],
        flush=True,
    )


    ema19 = calculate_ema(
        prices,
        19,
    )

    ema50 = calculate_ema(
        prices,
        50,
    )

    ema200 = calculate_ema(
        prices,
        200,
    )


    print(
        "INITIAL EMA ENGINE",
        flush=True,
    )

    print(
        "EMA19:",
        round(ema19, 2),
        flush=True,
    )

    print(
        "EMA50:",
        round(ema50, 2),
        flush=True,
    )

    print(
        "EMA200:",
        round(ema200, 2),
        flush=True,
    )


    structure = get_ema_structure(
        ema19,
        ema50,
        ema200,
    )


    print(
        "STRUCTURE:",
        structure,
        flush=True,
    )

    print(
        "EMA CROSSOVER DETECTOR READY",
        flush=True,
    )


    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )


    await send_telegram(
        bot,
        "✅ MODULE 0E-3 ONLINE\n"
        "BTCUSDT 1m EMA engine\n\n"
        "EMA19 / EMA50 / EMA200\n"
        "Crossover detector active\n\n"
        f"{structure}",
    )


    await run_websocket(
        bot,
        prices,
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )



# ==

        type(
# 
