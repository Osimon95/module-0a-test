import asyncio
import json
import os
import time
from decimal import Decimal, InvalidOperation
from typing import Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE 0E-2
# BTCUSDT 1-MINUTE EMA ENGINE
# EMA19 / EMA50 / EMA200
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

INTERVAL = "1m"

PRICE_TYPE = "LAST_PRICE"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIPTION_CHANNEL = (
    f"{SYMBOL}@kline_{INTERVAL}_{PRICE_TYPE}"
)

REST_KLINE_URL = (
    "https://api-contract.weex.com"
    "/capi/v3/market/klines"
)

HISTORICAL_CANDLE_LIMIT = 250


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


# ============================================================
# RECONNECT SETTINGS
# ============================================================

RECONNECT_DELAY_SECONDS = 5

MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# EMA PERIODS
# ============================================================

EMA19_PERIOD = 19

EMA50_PERIOD = 50

EMA200_PERIOD = 200


# ============================================================
# GLOBAL EMA VALUES
# ============================================================

ema19: Optional[Decimal] = None

ema50: Optional[Decimal] = None

ema200: Optional[Decimal] = None


previous_ema19: Optional[Decimal] = None

previous_ema50: Optional[Decimal] = None

previous_ema200: Optional[Decimal] = None


previous_structure: Optional[str] = None


# ============================================================
# LIVE CANDLE STATE
# ============================================================

current_live_candle_start: Optional[int] = None

current_live_candle_close: Optional[Decimal] = None


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
# DECIMAL HELPER
# ============================================================

def to_decimal(
    value,
) -> Optional[Decimal]:

    try:

        price = Decimal(str(value))

        if price <= 0:

            return None

        return price

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# HISTORICAL CANDLE LOADER
# ============================================================

async def load_historical_closes():

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": HISTORICAL_CANDLE_LIMIT,
    }

    headers = {
        "User-Agent": "WEEX-BTC-Bot/1.0",
    }

    timeout = aiohttp.ClientTimeout(
        total=20,
    )

    closes = []

    try:

        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
        ) as session:

            async with session.get(
                REST_KLINE_URL,
                params=params,
            ) as response:

                print(
                    f"HISTORICAL HTTP STATUS: "
                    f"{response.status}",
                    flush=True,
                )

                raw_text = await response.text()

                if response.status != 200:

                    print(
                        "HISTORICAL REQUEST FAILED",
                        flush=True,
                    )

                    print(
                        "RESPONSE:",
                        raw_text[:500],
                        flush=True,
                    )

                    return []

                try:

                    data = json.loads(raw_text)

                except json.JSONDecodeError:

                    print(
                        "ERROR: HISTORICAL RESPONSE "
                        "IS NOT VALID JSON",
                        flush=True,
                    )

                    print(
                        raw_text[:500],
                        flush=True,
                    )

                    return []


        if not isinstance(data, list):

            print(
                "ERROR: UNEXPECTED HISTORICAL "
                "RESPONSE FORMAT",
                flush=True,
            )

            print(
                str(data)[:500],
                flush=True,
            )

            return []


        current_time_ms = int(
            time.time() * 1000
        )


        valid_candles = []

        for candle in data:

            if not isinstance(
                candle,
                (list, tuple),
            ):

                continue

            if len(candle) < 7:

                continue


            try:

                open_time = int(
                    candle[0]
                )

                close_time = int(
                    candle[6]
                )

            except (
                TypeError,
                ValueError,
            ):

                continue


            close_price = to_decimal(
                candle[4]
            )

            if close_price is None:

                continue


            # ----------------------------------------
            # Only use candles that have CLOSED.
            # This prevents the currently forming
            # 1-minute candle entering EMA history.
            # ----------------------------------------

            if close_time > current_time_ms:

                continue


            valid_candles.append(
                (
                    open_time,
                    close_price,
                )
            )


        # WEEX normally returns candles ordered
        # by time, but sorting guarantees correct
        # EMA calculation order.

        valid_candles.sort(
            key=lambda item: item[0]
        )


        for _, close_price in valid_candles:

            closes.append(
                close_price
            )


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


    except asyncio.TimeoutError:

        print(
            "ERROR: HISTORICAL REQUEST TIMED OUT",
            flush=True,
        )

        return []


    except aiohttp.ClientError as error:

        print(
            "HISTORICAL NETWORK ERROR: "
            f"{type(error).__name__}: "
            f"{error}",
            flush=True,
        )

        return []


    except Exception as error:

        print(
            "HISTORICAL LOADER ERROR: "
            f"{type(error).__name__}: "
            f"{error}",
            flush=True,
        )

        return []


# ============================================================
# EMA INITIALIZATION
# ============================================================

def calculate_initial_ema(
    prices,
    period: int,
) -> Optional[Decimal]:

    if len(prices) < period:

        return None


    period_decimal = Decimal(
        period
    )


    # Start EMA with SMA of the first N prices.

    initial_sma = (
        sum(prices[:period])
        / period_decimal
    )


    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )


    ema_value = initial_sma


    # Continue EMA through remaining prices.

    for price in prices[period:]:

        ema_value = (
            (
                price
                - ema_value
            )
            * multiplier
            + ema_value
        )


    return ema_value


# ============================================================
# UPDATE ONE EMA
# ============================================================

def update_ema(
    previous_ema: Decimal,
    close_price: Decimal,
    period: int,
) -> Decimal:

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )


    return (
        (
            close_price
            - previous_ema
        )
        * multiplier
        + previous_ema
    )


# ============================================================
# MARKET STRUCTURE
# ============================================================

def get_structure() -> str:

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):

        return "UNKNOWN"


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
        ema50 > ema200
    ):

        return (
            "🟡 BULLISH BASE "
            "EMA50 > EMA200"
        )


    if (
        ema50 < ema200
    ):

        return (
            "🟠 BEARISH BASE "
            "EMA50 < EMA200"
        )


    return "⚪ NEUTRAL"


# ============================================================
# CROSS DETECTION
# ============================================================

def detect_ema50_ema200_cross() -> Optional[str]:

    if (
        previous_ema50 is None
        or previous_ema200 is None
        or ema50 is None
        or ema200 is None
    ):

        return None


    # Golden Cross:
    # EMA50 was <= EMA200
    # and is now > EMA200.

    if (
        previous_ema50
        <= previous_ema200
        and ema50 > ema200
    ):

        return (
            "🟢 EMA50 / EMA200 GOLDEN CROSS"
        )


    # Death Cross:
    # EMA50 was >= EMA200
    # and is now < EMA200.

    if (
        previous_ema50
        >= previous_ema200
        and ema50 < ema200
    ):

        return (
            "🔴 EMA50 / EMA200 DEATH CROSS"
        )


    return None


# ============================================================
# EMA19 / EMA50 CROSS
# ============================================================

def detect_ema19_ema50_cross() -> Optional[str]:

    if (
        previous_ema19 is None
        or previous_ema50 is None
        or ema19 is None
        or ema50 is None
    ):

        return None


    if (
        previous_ema19
        <= previous_ema50
        and ema19 > ema50
    ):

        return (
            "🟢 EMA19 CROSSED ABOVE EMA50"
        )


    if (
        previous_ema19
        >= previous_ema50
        and ema19 < ema50
    ):

        return (
            "🔴 EMA19 CROSSED BELOW EMA50"
        )


    return None


# ============================================================
# PROCESS CLOSED 1-MINUTE CANDLE
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
    global previous_ema200

    global previous_structure


    # Save previous EMA state before updating.

    previous_ema19 = ema19

    previous_ema50 = ema50

    previous_ema200 = ema200


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


    structure = get_structure()


    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E-2 - CLOSED 1m CANDLE",
        flush=True,
    )

    print(
        f"{SYMBOL} CLOSE: "
        f"{close_price}",
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


    # ----------------------------------------
    # PRIMARY EMA50 / EMA200 CROSS
    # ----------------------------------------

    major_cross = (
        detect_ema50_ema200_cross()
    )


    if major_cross:

        print(
            major_cross,
            flush=True,
        )

        message = (
            f"{major_cross}\n\n"
            f"{SYMBOL} 1m\n"
            f"Close: {close_price}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            f"{structure}"
        )

        await send_telegram(
            bot,
            message,
        )


    # ----------------------------------------
    # FAST EMA19 / EMA50 CROSS
    # ----------------------------------------

    fast_cross = (
        detect_ema19_ema50_cross()
    )


    if fast_cross:

        print(
            fast_cross,
            flush=True,
        )

        message = (
            f"{fast_cross}\n\n"
            f"{SYMBOL} 1m\n"
            f"Close: {close_price}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            f"{structure}"
        )

        await send_telegram(
            bot,
            message,
        )


    # ----------------------------------------
    # STRUCTURE CHANGE
    # ----------------------------------------

    if (
        previous_structure is not None
        and structure != previous_structure
    ):

        print(
            "EMA STRUCTURE CHANGED",
            flush=True,
        )

        print(
            f"OLD: {previous_structure}",
            flush=True,
        )

        print(
            f"NEW: {structure}",
            flush=True,
        )


    previous_structure = structure


# ============================================================
# EXTRACT LIVE KLINE
# ============================================================

def extract_kline(
    message,
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
        TypeError,
        ValueError,
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
# HANDLE LIVE KLINE
# ============================================================

async def handle_live_kline(
    bot: Bot,
    candle_start: int,
    close_price: Decimal,
) -> None:

    global current_live_candle_start
    global current_live_candle_close


    # First live candle received.

    if current_live_candle_start is None:

        current_live_candle_start = (
            candle_start
        )

        current_live_candle_close = (
            close_price
        )

        print(
            "LIVE 1m CANDLE STARTED: "
            f"{close_price}",
            flush=True,
        )

        return


    # Same candle is still forming.
    # Update its latest close only.

    if (
        candle_start
        == current_live_candle_start
    ):

        current_live_candle_close = (
            close_price
        )

        return


    # ----------------------------------------
    # A new candle has appeared.
    #
    # Therefore the previous candle has
    # definitely closed.
    # ----------------------------------------

    if (
        candle_start
        > current_live_candle_start
    ):

        closed_price = (
            current_live_candle_close
        )


        if closed_price is not None:

            await process_closed_candle(
                bot,
                closed_price,
            )


        current_live_candle_start = (
            candle_start
        )

        current_live_candle_close = (
            close_price
        )

        print(
            "NEW LIVE 1m CANDLE: "
            f"{close_price}",
            flush=True,
        )


# ============================================================
# WEBSOCKET
# ============================================================

async def run_websocket(
    bot: Bot,
) -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    connection_notification_sent = False


    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": (
                        "WEEX-BTC-Bot/1.0"
                    )
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
                            "✅ MODULE 0E-2 ONLINE\n"
                            f"{SYMBOL} 1-minute EMA engine\n"
                            "EMA19 / EMA50 / EMA200\n"
                            "Watching EMA crosses"
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


                    if not isinstance(
                        message,
                        dict,
                    ):

                        continue


                    # --------------------------------
                    # WEEX APPLICATION PING
                    # --------------------------------

                    if (
                        message.get("event")
                        == "ping"
                    ):

                        pong_message = {
                            "method": "PONG",
                            "id": 1,
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


                    # Private-channel style ping
                    # supported defensively.

                    if (
                        message.get("type")
                        == "ping"
                    ):

                        pong_message = {
                            "method": "PONG",
                            "id": 1,
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


                    # --------------------------------
                    # SUBSCRIPTION ACKNOWLEDGEMENT
                    # --------------------------------

                    if (
                        message.get("id") == 1
                        and message.get("result")
                        is True
                    ):

                        print(
                            "SUBSCRIPTION CONFIRMED",
                            flush=True,
                        )

                        continue


                    if (
                        message.get("id") == 1
                        and message.get("result")
                        is False
                    ):

                        print(
                            "SUBSCRIPTION FAILED: "
                            f"{message}",
                            flush=True,
                        )

                        continue


                    # --------------------------------
                    # LIVE CANDLE
                    # --------------------------------

                    kline = extract_kline(
                        message
                    )


                    if kline is None:

                        continue


                    candle_start, close_price = (
                        kline
                    )


                    await handle_live_kline(
                        bot,
                        candle_start,
                        close_price,
                    )


        except asyncio.CancelledError:

            raise


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

    global ema19
    global ema50
    global ema200
    global previous_structure


    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0E-2 STARTING",
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


    historical_closes = (
        await load_historical_closes()
    )


    if len(
        historical_closes
    ) < EMA200_PERIOD:

        print(
            "ERROR: NOT ENOUGH "
            "HISTORICAL CANDLES "
            "FOR EMA200",
            flush=True,
        )

        print(
            "CANDLES AVAILABLE: "
            f"{len(historical_closes)}",
            flush=True,
        )

        return


    ema19 = calculate_initial_ema(
        historical_closes,
        EMA19_PERIOD,
    )


    ema50 = calculate_initial_ema(
        historical_closes,
        EMA50_PERIOD,
    )


    ema200 = calculate_initial_ema(
        historical_closes,
        EMA200_PERIOD,
    )


    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):

        print(
            "ERROR: EMA INITIALIZATION FAILED",
            flush=True,
        )

        return


    previous_structure = (
        get_structure()
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
        "STRUCTURE: "
        f"{previous_structure}",
        flush=True,
    )

    print(
        "EMA ENGINE READY",
        flush=True,
    )


    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )


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
            "MODULE 0E-2 STOPPED",
            flush=True,)
