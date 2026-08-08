import asyncio
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0E-3"


# ============================================================
# CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIPTION_CHANNEL = (
    f"{SYMBOL}@kline_1m_LAST_PRICE"
)

HISTORICAL_URL = (
    "https://api-contract.weex.com"
    "/capi/v3/market/klines"
)

HISTORICAL_LIMIT = 250


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


async def send_telegram(
    bot: Bot,
    message: str,
) -> None:

    if not telegram_is_configured():

        print(
            "TELEGRAM WARNING: "
            "Token or chat ID missing.",
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
            "TELEGRAM ERROR: "
            f"{type(error).__name__}: "
            f"{error}",
            flush=True,
        )


# ============================================================
# EMA SETTINGS
# ============================================================

EMA19_PERIOD = 19
EMA50_PERIOD = 50
EMA200_PERIOD = 200


def ema_multiplier(
    period: int,
) -> Decimal:

    return Decimal("2") / Decimal(
        period + 1
    )


EMA19_MULTIPLIER = ema_multiplier(
    EMA19_PERIOD
)

EMA50_MULTIPLIER = ema_multiplier(
    EMA50_PERIOD
)

EMA200_MULTIPLIER = ema_multiplier(
    EMA200_PERIOD
)


# ============================================================
# EMA CALCULATION
# ============================================================

def calculate_initial_ema(
    prices: list[Decimal],
    period: int,
) -> Decimal:

    if len(prices) < period:

        raise ValueError(
            f"Not enough prices for EMA{period}"
        )

    multiplier = ema_multiplier(period)

    first_prices = prices[:period]

    ema = (
        sum(first_prices)
        / Decimal(period)
    )

    for price in prices[period:]:

        ema = (
            price * multiplier
            + ema
            * (
                Decimal("1")
                - multiplier
            )
        )

    return ema


def update_ema(
    price: Decimal,
    previous_ema: Decimal,
    multiplier: Decimal,
) -> Decimal:

    return (
        price * multiplier
        + previous_ema
        * (
            Decimal("1")
            - multiplier
        )
    )


# ============================================================
# MARKET STRUCTURE
# ============================================================

def get_structure(
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

    if (
        ema19 > ema50
        and ema50 < ema200
    ):

        return (
            "🟡 EARLY BULLISH / "
            "RECOVERY STRUCTURE"
        )

    if (
        ema19 < ema50
        and ema50 > ema200
    ):

        return (
            "🟠 EARLY BEARISH / "
            "WEAKENING STRUCTURE"
        )

    return "⚪ MIXED EMA STRUCTURE"


# ============================================================
# HISTORICAL CANDLES
# ============================================================

async def load_historical_candles() -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    params = {
        "symbol": SYMBOL,
        "interval": "1m",
        "limit": HISTORICAL_LIMIT,
    }

    try:

        timeout = aiohttp.ClientTimeout(
            total=20
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                HISTORICAL_URL,
                params=params,
            ) as response:

                print(
                    "HISTORICAL HTTP STATUS: "
                    f"{response.status}",
                    flush=True,
                )

                if response.status != 200:

                    error_text = (
                        await response.text()
                    )

                    print(
                        "HISTORICAL ERROR RESPONSE: "
                        f"{error_text}",
                        flush=True,
                    )

                    return []

                data = await response.json()

    except Exception as error:

        print(
            "HISTORICAL REQUEST ERROR: "
            f"{type(error).__name__}: "
            f"{error}",
            flush=True,
        )

        return []

    if not isinstance(data, list):

        print(
            "INVALID HISTORICAL RESPONSE: "
            f"{data}",
            flush=True,
        )

        return []

    candles = []

    for candle in data:

        try:

            if not isinstance(candle, list):
                continue

            if len(candle) < 5:
                continue

            timestamp = int(
                candle[0]
            )

            close_price = Decimal(
                str(candle[4])
            )

            if close_price <= 0:
                continue

            candles.append(
                (
                    timestamp,
                    close_price,
                )
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
            IndexError,
        ):

            continue

    candles.sort(
        key=lambda item: item[0]
    )

    closes = [
        candle[1]
        for candle in candles
    ]

    print(
        "HISTORICAL CANDLES LOADED: "
        f"{len(closes)}",
        flush=True,
    )

    if closes:

        print(
            "LATEST CLOSED PRICE: "
            f"{closes[-1]}",
            flush=True,
        )

    return closes


# ============================================================
# WEBSOCKET CANDLE EXTRACTION
# ============================================================

def find_kline_data(
    message: Any,
) -> Optional[list]:

    if isinstance(message, dict):

        for key in (
            "data",
            "result",
        ):

            value = message.get(key)

            result = find_kline_data(
                value
            )

            if result is not None:
                return result

        for value in message.values():

            result = find_kline_data(
                value
            )

            if result is not None:
                return result

    elif isinstance(message, list):

        if (
            len(message) >= 5
            and isinstance(
                message[0],
                (
                    int,
                    float,
                    str,
                ),
            )
        ):

            try:

                Decimal(
                    str(message[4])
                )

                return message

            except Exception:

                pass

        for item in message:

            result = find_kline_data(
                item
            )

            if result is not None:
                return result

    return None


def extract_candle(
    message: Any,
) -> Optional[
    tuple[int, Decimal]
]:

    kline = find_kline_data(
        message
    )

    if kline is None:
        return None

    try:

        timestamp = int(
            float(kline[0])
        )

        close_price = Decimal(
            str(kline[4])
        )

        if close_price <= 0:
            return None

        return (
            timestamp,
            close_price,
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
        IndexError,
    ):

        return None


# ============================================================
# CROSSOVER DETECTION
# ============================================================

async def check_crossovers(
    bot: Bot,
    price: Decimal,
    previous_ema19: Decimal,
    previous_ema50: Decimal,
    previous_ema200: Decimal,
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> None:

    # --------------------------------------------------------
    # EMA19 / EMA50 BULLISH CROSS
    # --------------------------------------------------------

    if (
        previous_ema19
        <= previous_ema50
        and ema19 > ema50
    ):

        message = (
            "🟢 EMA19 / EMA50 BULLISH CROSS\n\n"
            f"{SYMBOL}\n"
            f"Price: {price}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            "EMA19 crossed ABOVE EMA50."
        )

        print(
            "CROSSOVER DETECTED: "
            "EMA19 ABOVE EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            message,
        )

    # --------------------------------------------------------
    # EMA19 / EMA50 BEARISH CROSS
    # --------------------------------------------------------

    if (
        previous_ema19
        >= previous_ema50
        and ema19 < ema50
    ):

        message = (
            "🔴 EMA19 / EMA50 BEARISH CROSS\n\n"
            f"{SYMBOL}\n"
            f"Price: {price}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            "EMA19 crossed BELOW EMA50."
        )

        print(
            "CROSSOVER DETECTED: "
            "EMA19 BELOW EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            message,
        )

    # --------------------------------------------------------
    # EMA50 / EMA200 GOLDEN CROSS
    # --------------------------------------------------------

    if (
        previous_ema50
        <= previous_ema200
        and ema50 > ema200
    ):

        message = (
            "🚀 GOLDEN CROSS\n\n"
            f"{SYMBOL}\n"
            f"Price: {price}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            "EMA50 crossed ABOVE EMA200."
        )

        print(
            "CROSSOVER DETECTED: "
            "EMA50 ABOVE EMA200",
            flush=True,
        )

        await send_telegram(
            bot,
            message,
        )

    # --------------------------------------------------------
    # EMA50 / EMA200 DEATH CROSS
    # --------------------------------------------------------

    if (
        previous_ema50
        >= previous_ema200
        and ema50 < ema200
    ):

        message = (
            "⚠️ DEATH CROSS\n\n"
            f"{SYMBOL}\n"
            f"Price: {price}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            "EMA50 crossed BELOW EMA200."
        )

        print(
            "CROSSOVER DETECTED: "
            "EMA50 BELOW EMA200",
            flush=True,
        )

        await send_telegram(
            bot,
            message,
        )


# ============================================================
# SIMULATED CROSSOVER TEST
# ============================================================

async def run_simulated_crossover_test(
    bot: Bot,
) -> None:

    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E-3 SIMULATED CROSSOVER TEST",
        flush=True,
    )

    print(
        "SIMULATING EMA19 / EMA50 "
        "BULLISH CROSS...",
        flush=True,
    )

    # Before crossover:
    #
    # EMA19 is BELOW EMA50.
    #
    # After crossover:
    #
    # EMA19 is ABOVE EMA50.

    previous_ema19 = Decimal(
        "64990"
    )

    previous_ema50 = Decimal(
        "65000"
    )

    previous_ema200 = Decimal(
        "64900"
    )

    ema19 = Decimal(
        "65010"
    )

    ema50 = Decimal(
        "65000"
    )

    ema200 = Decimal(
        "64900"
    )

    test_price = Decimal(
        "65020"
    )

    await check_crossovers(
        bot,
        test_price,
        previous_ema19,
        previous_ema50,
        previous_ema200,
        ema19,
        ema50,
        ema200,
    )

    print(
        "SIMULATED CROSSOVER TEST COMPLETE",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )


# ============================================================
# WEBSOCKET
# ============================================================

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


async def run_websocket(
    bot: Bot,
    initial_ema19: Decimal,
    initial_ema50: Decimal,
    initial_ema200: Decimal,
) -> None:

    ema19 = initial_ema19
    ema50 = initial_ema50
    ema200 = initial_ema200

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    last_candle_timestamp = None

    current_candle_close = None

    connection_notification_sent = False

    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                    "WEEX-BTC-EMA-Bot/1.0"
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
                    "SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}",
                    flush=True,
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                if not connection_notification_sent:

                    await send_telegram(
                        bot,
                        (
                            "✅ MODULE 0E-3 ONLINE\n"
                            f"{SYMBOL} 1m EMA Engine\n"
                            "EMA19 / EMA50 / EMA200\n"
                            "Crossover detection active"
                        ),
                    )

                    connection_notification_sent = True

                async for raw_message in websocket:

                    try:

                        message = json.loads(
                            raw_message
                        )

                    except json.JSONDecodeError:

                        continue

                    # ----------------------------------------
                    # WEEX APPLICATION HEARTBEAT
                    # ----------------------------------------

                    if isinstance(
                        message,
                        dict,
                    ):

                        event = str(
                            message.get(
                                "event",
                                "",
                            )
                        ).lower()

                        method = str(
                            message.get(
                                "method",
                                "",
                            )
                        ).lower()

                        if (
                            event == "ping"
                            or method == "ping"
                        ):

                            try:

                                await websocket.send(
                                    json.dumps(
                                        {
                                            "method":
                                            "PONG"
                                        }
                                    )
                                )

                                print(
                                    "APPLICATION PONG SENT",
                                    flush=True,
                                )

                            except Exception:

                                pass

                            continue

                        message_text = str(
                            message
                        ).lower()

                        if (
                            "subscribe"
                            in message_text
                            and (
                                "success"
                                in message_text
                                or "result"
                                in message
                            )
                        ):

                            print(
                                "SUBSCRIPTION CONFIRMED",
                                flush=True,
                            )

                    # ----------------------------------------
                    # EXTRACT LIVE CANDLE
                    # ----------------------------------------

                    candle = extract_candle(
                        message
                    )

                    if candle is None:
                        continue

                    (
                        candle_timestamp,
                        close_price,
                    ) = candle

                    # ----------------------------------------
                    # FIRST LIVE CANDLE
                    # ----------------------------------------

                    if last_candle_timestamp is None:

                        last_candle_timestamp = (
                            candle_timestamp
                        )

                        current_candle_close = (
                            close_price
                        )

                        print(
                            "LIVE 1m CANDLE STARTED: "
                            f"{close_price}",
                            flush=True,
                        )

                        continue

                    # ----------------------------------------
                    # SAME OPEN CANDLE
                    # ----------------------------------------

                    if (
                        candle_timestamp
                        == last_candle_timestamp
                    ):

                        current_candle_close = (
                            close_price
                        )

                        continue

                    # ----------------------------------------
                    # PREVIOUS CANDLE HAS CLOSED
                    # ----------------------------------------

                    if (
                        candle_timestamp
                        > last_candle_timestamp
                        and current_candle_close
                        is not None
                    ):

                        closed_price = (
                            current_candle_close
                        )

                        previous_ema19 = ema19
                        previous_ema50 = ema50
                        previous_ema200 = ema200

                        ema19 = update_ema(
                            closed_price,
                            ema19,
                            EMA19_MULTIPLIER,
                        )

                        ema50 = update_ema(
                            closed_price,
                            ema50,
                            EMA50_MULTIPLIER,
                        )

                        ema200 = update_ema(
                            closed_price,
                            ema200,
                            EMA200_MULTIPLIER,
                        )

                        structure = get_structure(
                            ema19,
                            ema50,
                            ema200,
                        )

                        print(
                            "========================================",
                            flush=True,
                        )

                        print(
                            "MODULE 0E-3 - "
                            "CLOSED 1m CANDLE",
                            flush=True,
                        )

                        print(
                            f"{SYMBOL} CLOSE: "
                            f"{closed_price}",
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

                        print(
                            "STRUCTURE: "
                            f"{structure}",
                            flush=True,
                        )

                        await check_crossovers(
                            bot,
                            closed_price,
                            previous_ema19,
                            previous_ema50,
                            previous_ema200,
                            ema19,
                            ema50,
                            ema200,
                        )

                        print(
                            "NEW LIVE 1m CANDLE: "
                            f"{close_price}",
                            flush=True,
                        )

                    last_candle_timestamp = (
                        candle_timestamp
                    )

                    current_candle_close = (
                        close_price
                    )

        except Exception as error:

            print(
                "CONNECTION ERROR: "
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )

            print(
                "RECONNECTING IN "
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

    # ========================================================
    # LOAD HISTORY
    # ========================================================

    closes = await load_historical_candles()

    if len(closes) < EMA200_PERIOD:

        print(
            "ERROR: NOT ENOUGH "
            "HISTORICAL CANDLES "
            "FOR EMA200",
            flush=True,
        )

        return

    # ========================================================
    # INITIAL EMA ENGINE
    # ========================================================

    ema19 = calculate_initial_ema(
        closes,
        EMA19_PERIOD,
    )

    ema50 = calculate_initial_ema(
        closes,
        EMA50_PERIOD,
    )

    ema200 = calculate_initial_ema(
        closes,
        EMA200_PERIOD,
    )

    structure = get_structure(
        ema19,
        ema50,
        ema200,
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

    print(
        f"STRUCTURE: {structure}",
        flush=True,
    )

    print(
        "EMA ENGINE READY",
        flush=True,
    )

    # ========================================================
    # TELEGRAM BOT
    # ========================================================

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    # ========================================================
    # SIMULATED CROSSOVER TEST
    #
    # TEMPORARY:
    # This deliberately creates a fake EMA19/EMA50
    # bullish crossover so we can prove the
    # crossover -> Telegram alert path works.
    # ========================================================

    await run_simulated_crossover_test(
        bot
    )

    # ========================================================
    # START REAL LIVE 0E-3 ENGINE
    # ========================================================

    await run_websocket(
        bot,
        ema19,
        ema50,
        ema200,
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
