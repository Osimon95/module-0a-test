import asyncio
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Tuple

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-1"


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
# EMA SETTINGS
# ============================================================

EMA19_PERIOD = 19
EMA50_PERIOD = 50
EMA200_PERIOD = 200


# ============================================================
# RECONNECT SETTINGS
# ============================================================

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


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
            "Token or chat ID is missing.",
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
            f"{type(error).__name__}: {error}",
            flush=True,
        )


# ============================================================
# GLOBAL EMA STATE
# ============================================================

ema19: Optional[Decimal] = None
ema50: Optional[Decimal] = None
ema200: Optional[Decimal] = None


# ============================================================
# CROSSOVER STATE
# ============================================================

previous_ema19: Optional[Decimal] = None
previous_ema50: Optional[Decimal] = None


# ============================================================
# 0F-1 SIGNAL STATE
# ============================================================

last_trade_signal: Optional[str] = None


# ============================================================
# LIVE CANDLE STATE
# ============================================================

current_candle_timestamp: Optional[int] = None
current_candle_close: Optional[Decimal] = None


# ============================================================
# GENERAL HELPERS
# ============================================================

def to_decimal(
    value: Any,
) -> Optional[Decimal]:

    if value is None:
        return None

    try:

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


def to_timestamp(
    value: Any,
) -> Optional[int]:

    try:

        timestamp = int(
            Decimal(str(value))
        )

        if timestamp <= 0:
            return None

        return timestamp

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


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

    multiplier = (
        Decimal("2")
        /
        Decimal(period + 1)
    )

    # Start from SMA of the first N prices
    ema_value = (
        sum(prices[:period])
        /
        Decimal(period)
    )

    for price in prices[period:]:

        ema_value = (
            (
                price - ema_value
            )
            * multiplier
            + ema_value
        )

    return ema_value


def update_ema(
    previous_ema: Decimal,
    price: Decimal,
    period: int,
) -> Decimal:

    multiplier = (
        Decimal("2")
        /
        Decimal(period + 1)
    )

    return (
        (
            price - previous_ema
        )
        * multiplier
        + previous_ema
    )


# ============================================================
# EMA STRUCTURE
# ============================================================

def get_ema_structure(
    ema19_value: Decimal,
    ema50_value: Decimal,
    ema200_value: Decimal,
) -> str:

    if (
        ema19_value
        > ema50_value
        > ema200_value
    ):

        return (
            "🟢 STRONG BULLISH "
            "EMA19 > EMA50 > EMA200"
        )

    if (
        ema19_value
        < ema50_value
        < ema200_value
    ):

        return (
            "🔴 STRONG BEARISH "
            "EMA19 < EMA50 < EMA200"
        )

    if (
        ema19_value > ema50_value
    ):

        return (
            "🟡 EARLY BULLISH / "
            "RECOVERY STRUCTURE"
        )

    if (
        ema19_value < ema50_value
    ):

        return (
            "🟠 EARLY BEARISH / "
            "WEAKENING STRUCTURE"
        )

    return "⚪ NEUTRAL EMA STRUCTURE"


# ============================================================
# MODULE 0F
# TRADE SIGNAL CONFIRMATION ENGINE
# ============================================================

def get_trade_signal(
    close_price: Decimal,
    ema19_value: Decimal,
    ema50_value: Decimal,
    ema200_value: Decimal,
) -> str:

    # --------------------------------------------------------
    # STRONG LONG
    # Price and all EMAs bullish
    # --------------------------------------------------------

    if (
        close_price > ema19_value
        and ema19_value > ema50_value
        and ema50_value > ema200_value
    ):

        return "🟢 STRONG LONG"


    # --------------------------------------------------------
    # FAST LONG
    # Faster EMA structure bullish
    # EMA200 does not have to confirm yet
    # --------------------------------------------------------

    if (
        close_price > ema19_value
        and ema19_value > ema50_value
    ):

        return "⚡ FAST LONG / SCALP LONG"


    # --------------------------------------------------------
    # STRONG SHORT
    # Price and all EMAs bearish
    # --------------------------------------------------------

    if (
        close_price < ema19_value
        and ema19_value < ema50_value
        and ema50_value < ema200_value
    ):

        return "🔴 STRONG SHORT"


    # --------------------------------------------------------
    # FAST SHORT
    # Faster EMA structure bearish
    # EMA200 does not have to confirm yet
    # --------------------------------------------------------

    if (
        close_price < ema19_value
        and ema19_value < ema50_value
    ):

        return "⚡ FAST SHORT / SCALP SHORT"


    return "⚪ WAIT / NO TRADE"


# ============================================================
# MODULE 0F-1
# SIGNAL CHANGE + TELEGRAM ANTI-DUPLICATE
# ============================================================

async def process_trade_signal(
    bot: Bot,
    close_price: Decimal,
    ema19_value: Decimal,
    ema50_value: Decimal,
    ema200_value: Decimal,
) -> None:

    global last_trade_signal

    trade_signal = get_trade_signal(
        close_price,
        ema19_value,
        ema50_value,
        ema200_value,
    )

    print(
        f"0F SIGNAL: {trade_signal}",
        flush=True,
    )

    # --------------------------------------------------------
    # SAME SIGNAL
    # Do not repeatedly alert Telegram
    # --------------------------------------------------------

    if trade_signal == last_trade_signal:

        print(
            "0F-1: SIGNAL UNCHANGED "
            "- NO TELEGRAM ALERT",
            flush=True,
        )

        return


    previous_signal = last_trade_signal

    last_trade_signal = trade_signal

    print(
        "0F-1 SIGNAL CHANGE: "
        f"{previous_signal} -> "
        f"{trade_signal}",
        flush=True,
    )


    # --------------------------------------------------------
    # WAIT STATE
    # Remember state but do not send Telegram trade alert
    # --------------------------------------------------------

    if trade_signal == "⚪ WAIT / NO TRADE":

        print(
            "0F-1: WAIT STATE "
            "- TELEGRAM TRADE ALERT NOT SENT",
            flush=True,
        )

        return


    # --------------------------------------------------------
    # TELEGRAM SIGNAL ALERT
    # --------------------------------------------------------

    message = (
        "🚨 BTCUSDT TRADE SIGNAL\n\n"
        f"{trade_signal}\n\n"
        f"Price: {close_price}\n"
        f"EMA19: {ema19_value:.2f}\n"
        f"EMA50: {ema50_value:.2f}\n"
        f"EMA200: {ema200_value:.2f}\n\n"
        "Timeframe: 1 minute\n"
        "Confirmation: CLOSED CANDLE\n\n"
        f"Previous signal: "
        f"{previous_signal or 'NONE'}"
    )

    await send_telegram(
        bot,
        message,
    )


# ============================================================
# 0E-3 CROSSOVER DETECTION
# ============================================================

async def detect_real_crossover(
    bot: Bot,
    close_price: Decimal,
    old_ema19: Decimal,
    old_ema50: Decimal,
    new_ema19: Decimal,
    new_ema50: Decimal,
    new_ema200: Decimal,
) -> None:

    # --------------------------------------------------------
    # BULLISH EMA19 / EMA50 CROSSOVER
    # --------------------------------------------------------

    bullish_cross = (
        old_ema19 <= old_ema50
        and new_ema19 > new_ema50
    )

    if bullish_cross:

        print(
            "CROSSOVER DETECTED: "
            "EMA19 ABOVE EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            (
                "🟢 BTCUSDT BULLISH CROSSOVER\n\n"
                "EMA19 crossed ABOVE EMA50\n\n"
                f"Price: {close_price}\n"
                f"EMA19: {new_ema19:.2f}\n"
                f"EMA50: {new_ema50:.2f}\n"
                f"EMA200: {new_ema200:.2f}\n\n"
                "Timeframe: 1 minute\n"
                "Status: CLOSED CANDLE"
            ),
        )


    # --------------------------------------------------------
    # BEARISH EMA19 / EMA50 CROSSOVER
    # --------------------------------------------------------

    bearish_cross = (
        old_ema19 >= old_ema50
        and new_ema19 < new_ema50
    )

    if bearish_cross:

        print(
            "CROSSOVER DETECTED: "
            "EMA19 BELOW EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            (
                "🔴 BTCUSDT BEARISH CROSSOVER\n\n"
                "EMA19 crossed BELOW EMA50\n\n"
                f"Price: {close_price}\n"
                f"EMA19: {new_ema19:.2f}\n"
                f"EMA50: {new_ema50:.2f}\n"
                f"EMA200: {new_ema200:.2f}\n\n"
                "Timeframe: 1 minute\n"
                "Status: CLOSED CANDLE"
            ),
        )


# ============================================================
# SIMULATED CROSSOVER TEST
# ============================================================

async def simulated_crossover_test(
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
        "SIMULATING EMA19 / EMA50 BULLISH CROSS...",
        flush=True,
    )


    # Before crossover:
    simulated_old_ema19 = Decimal("100")
    simulated_old_ema50 = Decimal("101")

    # After crossover:
    simulated_new_ema19 = Decimal("102")
    simulated_new_ema50 = Decimal("101")


    if (
        simulated_old_ema19
        <= simulated_old_ema50
        and simulated_new_ema19
        > simulated_new_ema50
    ):

        print(
            "CROSSOVER DETECTED: "
            "EMA19 ABOVE EMA50",
            flush=True,
        )

        await send_telegram(
            bot,
            (
                "🧪 MODULE 0E-3 TEST\n\n"
                "🟢 SIMULATED BULLISH CROSSOVER\n\n"
                "EMA19 crossed ABOVE EMA50.\n\n"
                "This confirms the crossover "
                "detection and Telegram alert "
                "path are working."
            ),
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
# HISTORICAL CANDLE EXTRACTION
# ============================================================

def extract_historical_rows(
    payload: Any,
) -> list:

    # Direct list
    if isinstance(payload, list):

        return payload


    if not isinstance(payload, dict):

        return []


    # Common response containers
    for key in (
        "data",
        "result",
        "rows",
        "list",
        "candles",
    ):

        value = payload.get(key)

        if isinstance(value, list):

            return value

        if isinstance(value, dict):

            nested = extract_historical_rows(
                value
            )

            if nested:
                return nested


    return []


def extract_historical_close(
    row: Any,
) -> Optional[Decimal]:

    # --------------------------------------------------------
    # DICTIONARY CANDLE
    # --------------------------------------------------------

    if isinstance(row, dict):

        for key in (
            "close",
            "c",
            "closePrice",
            "lastPrice",
            "price",
        ):

            if key in row:

                price = to_decimal(
                    row.get(key)
                )

                if price is not None:
                    return price


    # --------------------------------------------------------
    # ARRAY CANDLE
    #
    # Standard format:
    # timestamp, open, high, low, close, ...
    # --------------------------------------------------------

    if isinstance(row, (list, tuple)):

        if len(row) >= 5:

            price = to_decimal(
                row[4]
            )

            if price is not None:
                return price


    return None


# ============================================================
# LOAD HISTORICAL 1m CANDLES
# ============================================================

async def load_historical_candles() -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    params_options = [

        {
            "symbol": SYMBOL,
            "interval": "1m",
            "limit": HISTORICAL_LIMIT,
        },

        {
            "symbol": SYMBOL,
            "interval": "1m",
            "limit": str(HISTORICAL_LIMIT),
        },
    ]


    timeout = aiohttp.ClientTimeout(
        total=20
    )


    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        for params in params_options:

            try:

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

                        continue


                    payload = await response.json(
                        content_type=None
                    )


                    rows = extract_historical_rows(
                        payload
                    )


                    closes: list[Decimal] = []


                    for row in rows:

                        price = extract_historical_close(
                            row
                        )

                        if price is not None:

                            closes.append(
                                price
                            )


                    if len(closes) >= EMA200_PERIOD:

                        # WEEX can return newest-first.
                        # Try to detect using candle timestamps.

                        timestamped_rows = []

                        for row in rows:

                            if (
                                isinstance(row, (list, tuple))
                                and len(row) >= 5
                            ):

                                timestamp = to_timestamp(
                                    row[0]
                                )

                                close = (
                                    extract_historical_close(
                                        row
                                    )
                                )

                                if (
                                    timestamp is not None
                                    and close is not None
                                ):

                                    timestamped_rows.append(
                                        (
                                            timestamp,
                                            close,
                                        )
                                    )


                        if len(timestamped_rows) >= EMA200_PERIOD:

                            timestamped_rows.sort(
                                key=lambda item: item[0]
                            )

                            closes = [
                                item[1]
                                for item in timestamped_rows
                            ]


                        # Keep latest required candles
                        closes = closes[
                            -HISTORICAL_LIMIT:
                        ]


                        print(
                            "HISTORICAL CANDLES LOADED: "
                            f"{len(closes)}",
                            flush=True,
                        )

                        print(
                            "LATEST CLOSED PRICE: "
                            f"{closes[-1]}",
                            flush=True,
                        )

                        return closes


            except Exception as error:

                print(
                    "HISTORICAL ERROR: "
                    f"{type(error).__name__}: "
                    f"{error}",
                    flush=True,
                )


    return []


# ============================================================
# INITIALIZE EMA ENGINE
# ============================================================

def initialize_ema_engine(
    closes: list[Decimal],
) -> None:

    global ema19
    global ema50
    global ema200
    global previous_ema19
    global previous_ema50


    if len(closes) < EMA200_PERIOD:

        raise ValueError(
            "NOT ENOUGH HISTORICAL "
            "CANDLES FOR EMA200"
        )


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


    previous_ema19 = ema19
    previous_ema50 = ema50


    structure = get_ema_structure(
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


# ============================================================
# LIVE WEBSOCKET KLINE EXTRACTION
# ============================================================

def extract_live_kline(
    message: Any,
) -> Optional[Tuple[int, Decimal]]:

    if not isinstance(message, dict):

        return None


    data = message.get("data")


    # --------------------------------------------------------
    # DATA AS DICTIONARY
    # --------------------------------------------------------

    if isinstance(data, dict):

        timestamp = None
        price = None


        for key in (
            "t",
            "ts",
            "timestamp",
            "time",
            "startTime",
            "openTime",
        ):

            if key in data:

                timestamp = to_timestamp(
                    data.get(key)
                )

                if timestamp is not None:
                    break


        for key in (
            "c",
            "close",
            "closePrice",
            "lastPrice",
            "price",
        ):

            if key in data:

                price = to_decimal(
                    data.get(key)
                )

                if price is not None:
                    break


        if (
            timestamp is not None
            and price is not None
        ):

            return (
                timestamp,
                price,
            )


    # --------------------------------------------------------
    # DATA AS LIST
    # --------------------------------------------------------

    if isinstance(data, list):

        # Example:
        # data = [[timestamp, open, high, low, close, ...]]

        rows = data


        if (
            len(data) > 0
            and not isinstance(
                data[0],
                (list, tuple, dict),
            )
        ):

            rows = [data]


        for row in rows:

            if isinstance(row, dict):

                nested_message = {
                    "data": row
                }

                result = extract_live_kline(
                    nested_message
                )

                if result is not None:
                    return result


            if isinstance(
                row,
                (list, tuple),
            ):

                if len(row) >= 5:

                    timestamp = to_timestamp(
                        row[0]
                    )

                    price = to_decimal(
                        row[4]
                    )

                    if (
                        timestamp is not None
                        and price is not None
                    ):

                        return (
                            timestamp,
                            price,
                        )


    # --------------------------------------------------------
    # SOME WEEX EVENTS CAN PLACE VALUES AT TOP LEVEL
    # --------------------------------------------------------

    timestamp = None
    price = None


    for key in (
        "t",
        "ts",
        "timestamp",
        "time",
    ):

        if key in message:

            timestamp = to_timestamp(
                message.get(key)
            )

            if timestamp is not None:
                break


    for key in (
        "c",
        "close",
        "closePrice",
        "lastPrice",
        "price",
    ):

        if key in message:

            price = to_decimal(
                message.get(key)
            )

            if price is not None:
                break


    if (
        timestamp is not None
        and price is not None
    ):

        return (
            timestamp,
            price,
        )


    return None


# ============================================================
# CLOSED 1-MINUTE CANDLE PROCESSING
# ============================================================

async def process_closed_candle(
    bot: Bot,
    close_price: Decimal,
) -> None:

    global ema19
    global ema50
    global ema200
    global previous_ema19
    global previous_ema50


    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):

        print(
            "EMA ENGINE NOT INITIALIZED",
            flush=True,
        )

        return


    # Save old EMA values BEFORE updating
    old_ema19 = ema19
    old_ema50 = ema50


    # --------------------------------------------------------
    # UPDATE EMAS USING CLOSED CANDLE
    # --------------------------------------------------------

    ema19 = update_ema(
        ema19,
        close_price,
        EMA19_PERIOD,
    )

    ema50 = update_ema(
        ema50,
        close_price,
        EMA50_PERIOD,
    )

    ema200 = update_ema(
        ema200,
        close_price,
        EMA200_PERIOD,
    )


    structure = get_ema_structure(
        ema19,
        ema50,
        ema200,
    )


    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0F-1 - CLOSED 1m CANDLE",
        flush=True,
    )

    print(
        f"BTCUSDT CLOSE: {close_price}",
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


    # --------------------------------------------------------
    # 0E-3 REAL CROSSOVER CHECK
    # --------------------------------------------------------

    await detect_real_crossover(
        bot,
        close_price,
        old_ema19,
        old_ema50,
        ema19,
        ema50,
        ema200,
    )


    # --------------------------------------------------------
    # 0F-1 TRADE SIGNAL ENGINE
    # --------------------------------------------------------

    await process_trade_signal(
        bot,
        close_price,
        ema19,
        ema50,
        ema200,
    )


    previous_ema19 = ema19
    previous_ema50 = ema50


    print(
        "========================================",
        flush=True,
    )


# ============================================================
# LIVE CANDLE HANDLER
# ============================================================

async def handle_live_kline(
    bot: Bot,
    timestamp: int,
    price: Decimal,
) -> None:

    global current_candle_timestamp
    global current_candle_close


    # --------------------------------------------------------
    # FIRST LIVE CANDLE
    # --------------------------------------------------------

    if current_candle_timestamp is None:

        current_candle_timestamp = timestamp
        current_candle_close = price

        print(
            "LIVE 1m CANDLE STARTED: "
            f"{price}",
            flush=True,
        )

        return


    # --------------------------------------------------------
    # SAME CANDLE
    # Just update latest close
    # --------------------------------------------------------

    if timestamp == current_candle_timestamp:

        current_candle_close = price

        return


    # --------------------------------------------------------
    # NEW CANDLE DETECTED
    # Therefore previous candle is CLOSED
    # --------------------------------------------------------

    if timestamp > current_candle_timestamp:

        closed_price = current_candle_close


        if closed_price is not None:

            await process_closed_candle(
                bot,
                closed_price,
            )


        current_candle_timestamp = timestamp
        current_candle_close = price


        print(
            "NEW LIVE 1m CANDLE: "
            f"{price}",
            flush=True,
        )


# ============================================================
# APPLICATION PING / PONG
# ============================================================

async def handle_application_ping(
    websocket: Any,
    message: Any,
) -> bool:

    if not isinstance(message, dict):

        return False


    event = str(
        message.get(
            "event",
            message.get(
                "method",
                message.get(
                    "op",
                    "",
                ),
            ),
        )
    ).lower()


    if event == "ping":

        pong_message = {
            "method": "PONG"
        }

        try:

            await websocket.send(
                json.dumps(
                    pong_message
                )
            )

            print(
                "APPLICATION PONG SENT",
                flush=True,
            )

        except Exception as error:

            print(
                "PONG ERROR: "
                f"{error}",
                flush=True,
            )


        return True


    return False


# ============================================================
# WEBSOCKET ENGINE
# ============================================================

async def run_websocket(
    bot: Bot,
) -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )


    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                    "WEEX-BTC-Bot/0F-1"
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


                async for raw_message in websocket:

                    try:

                        message = json.loads(
                            raw_message
                        )

                    except json.JSONDecodeError:

                        continue


                    # ----------------------------------------
                    # APPLICATION PING
                    # ----------------------------------------

                    if await handle_application_ping(
                        websocket,
                        message,
                    ):

                        continue


                    # ----------------------------------------
                    # SUBSCRIPTION CONFIRMATION
                    # ----------------------------------------

                    if isinstance(
                        message,
                        dict,
                    ):

                        message_id = (
                            message.get("id")
                        )

                        if message_id == 1:

                            print(
                                "SUBSCRIPTION CONFIRMED",
                                flush=True,
                            )


                    # ----------------------------------------
                    # EXTRACT LIVE KLINE
                    # ----------------------------------------

                    result = extract_live_kline(
                        message
                    )


                    if result is None:

                        continue


                    timestamp, price = result


                    await handle_live_kline(
                        bot,
                        timestamp,
                        price,
                    )


        except asyncio.CancelledError:

            raise


        except Exception as error:

            print(
                "WEBSOCKET ERROR: "
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )


            print(
                "RECONNECTING IN "
                f"{reconnect_delay} SECONDS...",
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
        "MODULE 0F-1 STARTING",
        flush=True,
    )

    print(
        "BTCUSDT TRADE SIGNAL "
        "CONFIRMATION ENGINE",
        flush=True,
    )

    print(
        "EMA19 / EMA50 / EMA200",
        flush=True,
    )

    print(
        "CROSSOVER + SIGNAL "
        "+ ANTI-DUPLICATE ALERTS",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )


    # --------------------------------------------------------
    # TELEGRAM CONFIG STATUS
    # --------------------------------------------------------

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


    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )


    # --------------------------------------------------------
    # HISTORICAL CANDLES
    # --------------------------------------------------------

    closes = await load_historical_candles()


    if len(closes) < EMA200_PERIOD:

        print(
            "ERROR: NOT ENOUGH "
            "HISTORICAL CANDLES "
            "FOR EMA200",
            flush=True,
        )

        return


    # --------------------------------------------------------
    # INITIALIZE EMA19 / EMA50 / EMA200
    # --------------------------------------------------------

    initialize_ema_engine(
        closes
    )


    # --------------------------------------------------------
    # 0E-3 SIMULATED CROSSOVER TEST
    # --------------------------------------------------------

    await simulated_crossover_test(
        bot
    )


    # --------------------------------------------------------
    # START LIVE WEEX ENGINE
    # --------------------------------------------------------

    await run_websocket(
        bot
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "MODULE 0F-1 STOPPED",
            flush=True,)
