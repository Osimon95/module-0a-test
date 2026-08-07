import asyncio
import json
import os
import time
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import websockets
from telegram import Bot


# ============================================================
# MODULE 0E
# BTC 1-MINUTE EMA ENGINE
#
# EMA19
# EMA50
# EMA200
#
# PURPOSE:
# 1. Load historical BTC 1-minute candles
# 2. Calculate EMA19 / EMA50 / EMA200
# 3. Connect to WEEX live 1-minute candles
# 4. Update EMA only after a candle closes
# 5. Display current EMA structure
#
# Crossover Telegram alerts come in the NEXT stage.
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

TIMEFRAME = "1m"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

REST_KLINE_URL = (
    "https://api-contract.weex.com/capi/v3/market/klines"
)

KLINE_CHANNEL = (
    f"{SYMBOL}@kline_{TIMEFRAME}_LAST_PRICE"
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


# ============================================================
# EMA SETTINGS
# ============================================================

EMA19_PERIOD = 19

EMA50_PERIOD = 50

EMA200_PERIOD = 200

HISTORICAL_CANDLE_LIMIT = 250

MAX_STORED_CANDLES = 500


# ============================================================
# RECONNECT SETTINGS
# ============================================================

RECONNECT_DELAY_SECONDS = 5

MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# GLOBAL STATE
# ============================================================

closed_candles = []

current_candle_start: Optional[int] = None

current_candle_close: Optional[Decimal] = None

last_processed_candle_start: Optional[int] = None

connection_notification_sent = False


# ============================================================
# TELEGRAM FUNCTIONS
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
# DECIMAL CONVERSION
# ============================================================

def to_decimal(
    value: Any,
) -> Optional[Decimal]:

    try:

        if value is None:
            return None

        number = Decimal(
            str(value)
        )

        if number <= 0:
            return None

        return number

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
    prices,
    period: int,
) -> Optional[Decimal]:

    if len(prices) < period:

        return None

    period_decimal = Decimal(
        period
    )

    initial_prices = prices[
        :period
    ]

    initial_sma = (
        sum(initial_prices)
        / period_decimal
    )

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    ema = initial_sma

    for price in prices[
        period:
    ]:

        ema = (
            (
                price
                - ema
            )
            * multiplier
            + ema
        )

    return ema


# ============================================================
# GET ALL EMA VALUES
# ============================================================

def get_ema_values():

    ema19 = calculate_ema(
        closed_candles,
        EMA19_PERIOD,
    )

    ema50 = calculate_ema(
        closed_candles,
        EMA50_PERIOD,
    )

    ema200 = calculate_ema(
        closed_candles,
        EMA200_PERIOD,
    )

    return (
        ema19,
        ema50,
        ema200,
    )


# ============================================================
# DETERMINE EMA STRUCTURE
# ============================================================

def determine_ema_structure(
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
            "BELOW EMA200"
        )

    if (
        ema19 < ema50
        and ema50 > ema200
    ):

        return (
            "🟡 EARLY BEARISH / "
            "ABOVE EMA200"
        )

    return "⚪ MIXED"


# ============================================================
# DISPLAY EMA STATE
# ============================================================

def display_ema_state(
    candle_close: Decimal,
) -> None:

    ema19, ema50, ema200 = (
        get_ema_values()
    )

    print(
        "",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E - CLOSED 1m CANDLE",
        flush=True,
    )

    print(
        f"{SYMBOL} CLOSE: "
        f"{candle_close}",
        flush=True,
    )

    print(
        f"CANDLES STORED: "
        f"{len(closed_candles)}",
        flush=True,
    )

    if ema19 is None:

        print(
            "EMA19: WAITING",
            flush=True,
        )

    else:

        print(
            f"EMA19: "
            f"{ema19:.2f}",
            flush=True,
        )

    if ema50 is None:

        print(
            "EMA50: WAITING",
            flush=True,
        )

    else:

        print(
            f"EMA50: "
            f"{ema50:.2f}",
            flush=True,
        )

    if ema200 is None:

        print(
            "EMA200: WAITING",
            flush=True,
        )

    else:

        print(
            f"EMA200: "
            f"{ema200:.2f}",
            flush=True,
        )

    if (
        ema19 is not None
        and ema50 is not None
        and ema200 is not None
    ):

        structure = (
            determine_ema_structure(
                ema19,
                ema50,
                ema200,
            )
        )

        print(
            f"STRUCTURE: {structure}",
            flush=True,
        )

        gap_19_50 = (
            (
                ema19
                - ema50
            )
            / ema50
        ) * Decimal("100")

        gap_50_200 = (
            (
                ema50
                - ema200
            )
            / ema200
        ) * Decimal("100")

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

    print(
        "========================================",
        flush=True,
    )


# ============================================================
# REST DOWNLOAD
# ============================================================

def download_historical_klines():

    parameters = (
        urllib.parse.urlencode(
            {
                "symbol": SYMBOL,
                "interval": TIMEFRAME,
                "limit":
                    HISTORICAL_CANDLE_LIMIT,
            }
        )
    )

    url = (
        REST_KLINE_URL
        + "?"
        + parameters
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "WEEX-BTC-EMA-Bot/1.0"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:

        raw_data = response.read()

    return json.loads(
        raw_data.decode(
            "utf-8"
        )
    )


# ============================================================
# HISTORICAL CANDLE INITIALIZATION
# ============================================================

async def load_historical_candles() -> bool:

    global closed_candles
    global last_processed_candle_start

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    try:

        data = await asyncio.to_thread(
            download_historical_klines
        )

    except Exception as error:

        print(
            "HISTORICAL DATA ERROR: "
            f"{type(error).__name__}: "
            f"{error}",
            flush=True,
        )

        return False

    if not isinstance(
        data,
        list,
    ):

        print(
            "HISTORICAL DATA ERROR: "
            "Unexpected WEEX response.",
            flush=True,
        )

        print(
            data,
            flush=True,
        )

        return False

    parsed_candles = []

    for candle in data:

        if not isinstance(
            candle,
            list,
        ):

            continue

        if len(candle) < 5:

            continue

        try:

            candle_start = int(
                candle[0]
            )

        except (
            ValueError,
            TypeError,
        ):

            continue

        close_price = (
            to_decimal(
                candle[4]
            )
        )

        if close_price is None:

            continue

        parsed_candles.append(
            (
                candle_start,
                close_price,
            )
        )

    if not parsed_candles:

        print(
            "NO VALID HISTORICAL "
            "CANDLES RECEIVED.",
            flush=True,
        )

        return False

    parsed_candles.sort(
        key=lambda item: item[0]
    )

    # ========================================================
    # REMOVE CURRENT FORMING MINUTE
    # ========================================================

    current_time_ms = int(
        time.time() * 1000
    )

    current_minute_start = (
        current_time_ms
        // 60000
        * 60000
    )

    completed_candles = []

    for (
        candle_start,
        close_price,
    ) in parsed_candles:

        if (
            candle_start
            < current_minute_start
        ):

            completed_candles.append(
                (
                    candle_start,
                    close_price,
                )
            )

    if len(
        completed_candles
    ) < EMA200_PERIOD:

        print(
            "ERROR: LESS THAN 200 "
            "COMPLETED CANDLES RECEIVED.",
            flush=True,
        )

        return False

    closed_candles = [
        close_price
        for (
            candle_start,
            close_price,
        )
        in completed_candles
    ]

    last_processed_candle_start = (
        completed_candles[-1][0]
    )

    print(
        f"HISTORICAL CANDLES LOADED: "
        f"{len(closed_candles)}",
        flush=True,
    )

    print(
        f"LATEST CLOSED PRICE: "
        f"{closed_candles[-1]}",
        flush=True,
    )

    ema19, ema50, ema200 = (
        get_ema_values()
    )

    print(
        "",
        flush=True,
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

    structure = (
        determine_ema_structure(
            ema19,
            ema50,
            ema200,
        )
    )

    print(
        f"STRUCTURE: {structure}",
        flush=True,
    )

    print(
        "EMA ENGINE READY",
        flush=True,
    )

    return True


# ============================================================
# EXTRACT WEEX KLINE
# ============================================================

def extract_kline(
    message: Any,
):

    if not isinstance(
        message,
        dict,
    ):

        return None

    if message.get("e") != "kline":

        return None

    data = message.get("d")

    if not isinstance(
        data,
        list,
    ):

        return None

    if not data:

        return None

    candle = data[0]

    if not isinstance(
        candle,
        dict,
    ):

        return None

    try:

        candle_start = int(
            candle.get("t")
        )

    except (
        ValueError,
        TypeError,
    ):

        return None

    close_price = to_decimal(
        candle.get("c")
    )

    if close_price is None:

        return None

    return (
        candle_start,
        close_price,
    )


# ============================================================
# PROCESS LIVE CANDLE
# ============================================================

def process_live_candle(
    candle_start: int,
    close_price: Decimal,
) -> None:

    global current_candle_start
    global current_candle_close
    global last_processed_candle_start
    global closed_candles

    # ========================================================
    # FIRST LIVE CANDLE
    # ========================================================

    if current_candle_start is None:

        current_candle_start = (
            candle_start
        )

        current_candle_close = (
            close_price
        )

        print(
            f"LIVE 1m CANDLE STARTED: "
            f"{close_price}",
            flush=True,
        )

        return

    # ========================================================
    # SAME CANDLE STILL FORMING
    # ========================================================

    if (
        candle_start
        == current_candle_start
    ):

        current_candle_close = (
            close_price
        )

        return

    # ========================================================
    # NEW MINUTE
    #
    # PREVIOUS CANDLE IS NOW CLOSED
    # ========================================================

    if (
        candle_start
        > current_candle_start
    ):

        closed_start = (
            current_candle_start
        )

        closed_price = (
            current_candle_close
        )

        if (
            closed_price is not None
            and (
                last_processed_candle_start
                is None
                or closed_start
                > last_processed_candle_start
            )
        ):

            closed_candles.append(
                closed_price
            )

            if (
                len(closed_candles)
                > MAX_STORED_CANDLES
            ):

                closed_candles = (
                    closed_candles[
                        -MAX_STORED_CANDLES:
                    ]
                )

            last_processed_candle_start = (
                closed_start
            )

            display_ema_state(
                closed_price
            )

        current_candle_start = (
            candle_start
        )

        current_candle_close = (
            close_price
        )


# ============================================================
# WEEX WEBSOCKET
# ============================================================

async def run_websocket(
    bot: Bot,
) -> None:

    global connection_notification_sent

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

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
                        KLINE_CHANNEL
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
                    f"{KLINE_CHANNEL}",
                    flush=True,
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                if (
                    not
                    connection_notification_sent
                ):

                    await send_telegram(
                        bot,
                        (
                            "✅ MODULE 0E CONNECTED\n"
                            "\n"
                            "BTCUSDT 1-minute EMA engine\n"
                            "EMA19 ✅\n"
                            "EMA50 ✅\n"
                            "EMA200 ✅"
                        ),
                    )

                    connection_notification_sent = (
                        True
                    )

                async for raw_message in websocket:

                    # =================================================
                    # TEXT PING
                    # =================================================

                    if (
                        isinstance(
                            raw_message,
                            str,
                        )
                        and raw_message.lower()
                        == "ping"
                    ):

                        await websocket.send(
                            "pong"
                        )

                        print(
                            "APPLICATION PONG SENT",
                            flush=True,
                        )

                        continue

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

                    # =================================================
                    # SUBSCRIPTION CONFIRMATION
                    # =================================================

                    if (
                        "result" in message
                        and "id" in message
                    ):

                        if (
                            message.get(
                                "result"
                            )
                            is True
                        ):

                            print(
                                "SUBSCRIPTION CONFIRMED",
                                flush=True,
                            )

                        else:

                            print(
                                "SUBSCRIPTION ERROR: "
                                f"{message}",
                                flush=True,
                            )

                        continue

                    # =================================================
                    # JSON PING
                    # =================================================

                    if (
                        message.get("ping")
                        is not None
                    ):

                        pong_message = {
                            "pong":
                                message.get(
                                    "ping"
                                )
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

                    # =================================================
                    # KLINE
                    # =================================================

                    kline = extract_kline(
                        message
                    )

                    if kline is None:

                        continue

                    (
                        candle_start,
                        close_price,
                    ) = kline

                    process_live_candle(
                        candle_start,
                        close_price,
                    )

        except Exception as error:

            print(
                "CONNECTION ERROR: "
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
        "",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E STARTING",
        flush=True,
    )

    print(
        "BTCUSDT 1-MINUTE EMA ENGINE",
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

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN or "
            "TELEGRAM_CHAT_ID is missing."
        )

    historical_ready = False

    while not historical_ready:

        historical_ready = (
            await load_historical_candles()
        )

        if not historical_ready:

            print(
                "RETRYING HISTORICAL DATA "
                "IN 10 SECONDS...",
                flush=True,
            )

            await asyncio.sleep(
                10
            )

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    await run_websocket(
        bot
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
