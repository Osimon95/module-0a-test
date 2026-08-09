import asyncio
import json
import os
import time
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-2"


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

# Request 251 so we can retain 250 fully closed candles.
HISTORICAL_REQUEST_LIMIT = 251

HISTORICAL_LIMIT = 250

RECONNECT_DELAY_SECONDS = 5

MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# EMA SETTINGS
# ============================================================

EMA19_PERIOD = 19
EMA50_PERIOD = 50
EMA200_PERIOD = 200


# ============================================================
# SIMULATED VERIFICATION TEST
# ============================================================

# IMPORTANT:
#
# Leave True for the FIRST deployment.
#
# After Telegram receives the simulated confirmation message,
# change this to False and redeploy.

RUN_SIMULATED_PENDING_TEST = False


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
            "TELEGRAM WARNING: Token or chat ID is missing.",
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

def calculate_initial_ema(
    prices: list[Decimal],
    period: int,
) -> Decimal:

    if not prices:

        raise ValueError(
            "No prices supplied for EMA calculation."
        )

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    ema = prices[0]

    for price in prices[1:]:

        ema = (
            (price - ema)
            * multiplier
            + ema
        )

    return ema


def update_ema(
    previous_ema: Decimal,
    new_price: Decimal,
    period: int,
) -> Decimal:

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    return (
        (new_price - previous_ema)
        * multiplier
        + previous_ema
    )


# ============================================================
# EMA STRUCTURE
# ============================================================

def describe_structure(
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
        and ema50 <= ema200
    ):

        return (
            "🟡 EARLY BULLISH / "
            "RECOVERY STRUCTURE"
        )

    if (
        ema19 < ema50
        and ema50 >= ema200
    ):

        return (
            "🟠 EARLY BEARISH / "
            "WEAKENING STRUCTURE"
        )

    return "⚪ MIXED EMA STRUCTURE"


# ============================================================
# HISTORICAL CANDLES
# ============================================================

async def load_historical_candles(
    session: aiohttp.ClientSession,
) -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    params = {
        "symbol": SYMBOL,
        "interval": "1m",
        "limit": HISTORICAL_REQUEST_LIMIT,
    }

    try:

        async with session.get(
            HISTORICAL_URL,
            params=params,
            timeout=aiohttp.ClientTimeout(
                total=20
            ),
        ) as response:

            print(
                "HISTORICAL HTTP STATUS:",
                response.status,
                flush=True,
            )

            if response.status != 200:

                return []

            data = await response.json()

    except Exception as error:

        print(
            "HISTORICAL ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )

        return []

    # Some API responses may wrap the array.
    if isinstance(data, dict):

        for key in (
            "data",
            "result",
            "list",
        ):

            candidate = data.get(key)

            if isinstance(candidate, list):

                data = candidate
                break

    if not isinstance(data, list):

        print(
            "HISTORICAL ERROR: "
            "Unexpected response format.",
            flush=True,
        )

        return []

    candles = []

    now_ms = int(
        time.time() * 1000
    )

    for item in data:

        if not isinstance(
            item,
            (list, tuple),
        ):

            continue

        if len(item) < 7:

            continue

        try:

            open_time = int(
                item[0]
            )

            close_time = int(
                item[6]
            )

        except (
            ValueError,
            TypeError,
        ):

            continue

        close_price = to_decimal(
            item[4]
        )

        if close_price is None:

            continue

        # Keep only candles whose close time
        # has already passed.
        if close_time > now_ms:

            continue

        candles.append(
            (
                open_time,
                close_price,
            )
        )

    candles.sort(
        key=lambda candle: candle[0]
    )

    # Retain the most recent 250 closed candles.
    candles = candles[
        -HISTORICAL_LIMIT:
    ]

    closes = [
        candle[1]
        for candle in candles
    ]

    print(
        "HISTORICAL CANDLES LOADED:",
        len(closes),
        flush=True,
    )

    if closes:

        print(
            "LATEST CLOSED PRICE:",
            closes[-1],
            flush=True,
        )

    return closes


# ============================================================
# SIMULATED PENDING CONFIRMATION TEST
# ============================================================

async def run_simulated_pending_confirmation_test(
    bot: Bot,
) -> None:

    if not SIMULATED_PENDING_TEST_ENABLED:

        print(
            "SIMULATED TEST DISABLED",
            flush=True,
        )

        return

    print(
        "========================================",
        flush=True,
    )

    print(
        "MODULE 0F-2 SIMULATED PENDING TEST",
        flush=True,
    )

    print(
        "SIMULATING EMA19 / EMA50 "
        "BULLISH CROSS...",
        flush=True,
    )

    # ----------------------------------------
    # BEFORE CROSS
    # ----------------------------------------

    ema19_before = Decimal("100")

    ema50_before = Decimal("101")

    # ----------------------------------------
    # AFTER CROSS
    # ----------------------------------------

    ema19_after = Decimal("102")

    ema50_after = Decimal("101")

    bullish_cross = (
        ema19_before
        <= ema50_before
        and ema19_after
        > ema50_after
    )

    if not bullish_cross:

        print(
            "SIMULATED TEST FAILED: "
            "NO CROSSOVER",
            flush=True,
        )

        return

    print(
        "SIMULATED BULLISH CROSSOVER DETECTED",
        flush=True,
    )

    print(
        "SIMULATED SIGNAL STATUS: PENDING",
        flush=True,
    )

    # ----------------------------------------
    # NEXT CANDLE
    # ----------------------------------------

    confirmation_ema19 = Decimal(
        "103"
    )

    confirmation_ema50 = Decimal(
        "101.5"
    )

    confirmation_ema200 = Decimal(
        "99"
    )

    confirmed = (
        confirmation_ema19
        > confirmation_ema50
        > confirmation_ema200
    )

    if not confirmed:

        print(
            "SIMULATED SIGNAL REJECTED",
            flush=True,
        )

        return

    print(
        "SIMULATED SIGNAL CONFIRMED",
        flush=True,
    )

    message = (
        "🧪 MODULE 0F-2 TEST\n\n"
        "BTCUSDT\n\n"
        "✅ BULLISH CROSSOVER DETECTED\n"
        "⏳ SIGNAL ENTERED PENDING STATE\n"
        "✅ NEXT-CANDLE CONFIRMATION PASSED\n\n"
        "🟢 TEST LONG SIGNAL CONFIRMED\n\n"
        "EMA19 > EMA50 > EMA200\n\n"
        "This is a SIMULATED TEST only.\n"
        "No live trade signal was generated."
    )

    await send_telegram(
        bot,
        message,
    )

    print(
        "SIMULATED TELEGRAM ALERT SENT",
        flush=True,
    )

    print(
        "SIMULATED PENDING TEST COMPLETE",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )


# ============================================================
# SIGNAL ENGINE
# ============================================================

class SignalEngine:

    def __init__(
        self,
        ema19: Decimal,
        ema50: Decimal,
        ema200: Decimal,
        bot: Bot,
    ) -> None:

        self.ema19 = ema19

        self.ema50 = ema50

        self.ema200 = ema200

        self.previous_ema19 = ema19

        self.previous_ema50 = ema50

        self.bot = bot

        self.pending_signal: Optional[
            dict[str, Any]
        ] = None

        self.last_confirmed_signal: Optional[
            str
        ] = None


    async def process_closed_candle(
        self,
        close_price: Decimal,
        candle_time: int,
    ) -> None:

        # Save previous EMA19 / EMA50
        # for crossover detection.

        previous_ema19 = self.ema19

        previous_ema50 = self.ema50

        # Update all EMAs using the newly
        # closed 1-minute candle.

        self.ema19 = update_ema(
            self.ema19,
            close_price,
            EMA19_PERIOD,
        )

        self.ema50 = update_ema(
            self.ema50,
            close_price,
            EMA50_PERIOD,
        )

        self.ema200 = update_ema(
            self.ema200,
            close_price,
            EMA200_PERIOD,
        )

        print(
            "========================================",
            flush=True,
        )

        print(
            "MODULE 0F-2 - CLOSED 1m CANDLE",
            flush=True,
        )

        print(
            f"{SYMBOL} CLOSE: {close_price}",
            flush=True,
        )

        print(
            "EMA19:",
            round(self.ema19, 2),
            flush=True,
        )

        print(
            "EMA50:",
            round(self.ema50, 2),
            flush=True,
        )

        print(
            "EMA200:",
            round(self.ema200, 2),
            flush=True,
        )

        structure = describe_structure(
            self.ema19,
            self.ema50,
            self.ema200,
        )

        print(
            "STRUCTURE:",
            structure,
            flush=True,
        )

        # ====================================================
        # STEP 1
        # CONFIRM OR REJECT AN EXISTING PENDING SIGNAL
        #
        # This runs BEFORE checking for a new crossover.
        # Therefore a signal created on this candle cannot
        # be confirmed until the NEXT closed candle.
        # ====================================================

        if self.pending_signal is not None:

            await self.confirm_pending_signal(
                close_price=close_price,
                candle_time=candle_time,
            )

        # ====================================================
        # STEP 2
        # DETECT A NEW CROSSOVER
        # ====================================================

        bullish_cross = (
            previous_ema19
            <= previous_ema50
            and self.ema19
            > self.ema50
        )

        bearish_cross = (
            previous_ema19
            >= previous_ema50
            and self.ema19
            < self.ema50
        )

        if bullish_cross:

            print(
                "CROSSOVER DETECTED: "
                "EMA19 ABOVE EMA50",
                flush=True,
            )

            self.pending_signal = {
                "direction": "LONG",
                "created_time": candle_time,
                "price": close_price,
            }

            print(
                "LONG SIGNAL STATUS: PENDING",
                flush=True,
            )

            print(
                "WAITING FOR NEXT CLOSED "
                "1m CANDLE CONFIRMATION",
                flush=True,
            )

        elif bearish_cross:

            print(
                "CROSSOVER DETECTED: "
                "EMA19 BELOW EMA50",
                flush=True,
            )

            self.pending_signal = {
                "direction": "SHORT",
                "created_time": candle_time,
                "price": close_price,
            }

            print(
                "SHORT SIGNAL STATUS: PENDING",
                flush=True,
            )

            print(
                "WAITING FOR NEXT CLOSED "
                "1m CANDLE CONFIRMATION",
                flush=True,
            )

        self.previous_ema19 = self.ema19

        self.previous_ema50 = self.ema50


    async def confirm_pending_signal(
        self,
        close_price: Decimal,
        candle_time: int,
    ) -> None:

        if self.pending_signal is None:

            return

        direction = self.pending_signal.get(
            "direction"
        )

        created_time = self.pending_signal.get(
            "created_time"
        )

        # Do not confirm on the same candle
        # that created the pending signal.

        if candle_time == created_time:

            return

        if direction == "LONG":

            confirmed = (
                self.ema19
                > self.ema50
                > self.ema200
            )

            if confirmed:

                print(
                    "PENDING LONG SIGNAL CONFIRMED",
                    flush=True,
                )

                await self.send_live_signal(
                    direction="LONG",
                    close_price=close_price,
                )

            else:

                print(
                    "PENDING LONG SIGNAL REJECTED",
                    flush=True,
                )

                print(
                    "REASON: "
                    "EMA19 > EMA50 > EMA200 "
                    "NOT CONFIRMED",
                    flush=True,
                )

        elif direction == "SHORT":

            confirmed = (
                self.ema19
                < self.ema50
                < self.ema200
            )

            if confirmed:

                print(
                    "PENDING SHORT SIGNAL CONFIRMED",
                    flush=True,
                )

                await self.send_live_signal(
                    direction="SHORT",
                    close_price=close_price,
                )

            else:

                print(
                    "PENDING SHORT SIGNAL REJECTED",
                    flush=True,
                )

                print(
                    "REASON: "
                    "EMA19 < EMA50 < EMA200 "
                    "NOT CONFIRMED",
                    flush=True,
                )

        self.pending_signal = None


    async def send_live_signal(
        self,
        direction: str,
        close_price: Decimal,
    ) -> None:

        # Anti-duplicate protection.
        #
        # A fresh opposite crossover will be
        # required before the same directional
        # sequence can naturally occur again.

        if (
            self.last_confirmed_signal
            == direction
        ):

            print(
                "DUPLICATE SIGNAL BLOCKED:",
                direction,
                flush=True,
            )

            return

        self.last_confirmed_signal = direction

        if direction == "LONG":

            message = (
                "🟢 BTCUSDT LONG SIGNAL\n\n"
                "✅ EMA19 / EMA50 "
                "BULLISH CROSSOVER\n"
                "✅ NEXT 1m CANDLE CONFIRMED\n"
                "✅ EMA19 > EMA50 > EMA200\n\n"
                f"Price: {close_price}\n"
                f"EMA19: {self.ema19:.2f}\n"
                f"EMA50: {self.ema50:.2f}\n"
                f"EMA200: {self.ema200:.2f}\n\n"
                "MODULE 0F-2"
            )

        else:

            message = (
                "🔴 BTCUSDT SHORT SIGNAL\n\n"
                "✅ EMA19 / EMA50 "
                "BEARISH CROSSOVER\n"
                "✅ NEXT 1m CANDLE CONFIRMED\n"
                "✅ EMA19 < EMA50 < EMA200\n\n"
                f"Price: {close_price}\n"
                f"EMA19: {self.ema19:.2f}\n"
                f"EMA50: {self.ema50:.2f}\n"
                f"EMA200: {self.ema200:.2f}\n\n"
                "MODULE 0F-2"
            )

        await send_telegram(
            self.bot,
            message,
        )


# ============================================================
# WEBSOCKET MESSAGE HANDLING
# ============================================================

def extract_kline(
    message: Any,
) -> Optional[dict[str, Any]]:

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

        start_time = int(
            candle.get("t")
        )

        close_time = int(
            candle.get("T")
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

    return {
        "start_time": start_time,
        "close_time": close_time,
        "close_price": close_price,
    }


# ============================================================
# LIVE WEBSOCKET ENGINE
# ============================================================

async def run_live_engine(
    signal_engine: SignalEngine,
) -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    while True:

        try:

            async with websockets.connect(
                WS_URL,
                ping_interval=None,
                close_timeout=10,
            ) as websocket:

                print(
                    "CONNECTED TO WEEX",
                    flush=True,
                )

                subscription = {
                    "method": "SUBSCRIBE",
                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],
                    "id": 1,
                }

                await websocket.send(
                    json.dumps(
                        subscription
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

                live_candle_start: Optional[
                    int
                ] = None

                live_candle_close: Optional[
                    Decimal
                ] = None

                async for raw_message in websocket:

                    # ----------------------------------------
                    # TEXT PING
                    # ----------------------------------------

                    if raw_message == "ping":

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

                    except (
                        json.JSONDecodeError,
                        TypeError,
                    ):

                        continue

                    # ----------------------------------------
                    # SUBSCRIPTION ACK
                    # ----------------------------------------

                    if (
                        isinstance(message, dict)
                        and message.get("id") == 1
                        and message.get("result")
                        is True
                    ):

                        print(
                            "SUBSCRIPTION CONFIRMED",
                            flush=True,
                        )

                        continue

                    # ----------------------------------------
                    # JSON PING HANDLING
                    # ----------------------------------------

                    if isinstance(
                        message,
                        dict,
                    ):

                        if "ping" in message:

                            await websocket.send(
                                json.dumps(
                                    {
                                        "pong":
                                        message[
                                            "ping"
                                        ]
                                    }
                                )
                            )

                            print(
                                "APPLICATION PONG SENT",
                                flush=True,
                            )

                            continue

                        if (
                            str(
                                message.get(
                                    "event",
                                    ""
                                )
                            ).lower()
                            == "ping"
                        ):

                            await websocket.send(
                                json.dumps(
                                    {
                                        "event":
                                        "pong"
                                    }
                                )
                            )

                            print(
                                "APPLICATION PONG SENT",
                                flush=True,
                            )

                            continue

                    # ----------------------------------------
                    # EXTRACT KLINE
                    # ----------------------------------------

                    candle = extract_kline(
                        message
                    )

                    if candle is None:

                        continue

                    candle_start = candle[
                        "start_time"
                    ]

                    candle_close = candle[
                        "close_price"
                    ]

                    # ----------------------------------------
                    # FIRST LIVE CANDLE
                    # ----------------------------------------

                    if live_candle_start is None:

                        live_candle_start = (
                            candle_start
                        )

                        live_candle_close = (
                            candle_close
                        )

                        print(
                            "LIVE 1m CANDLE STARTED:",
                            candle_close,
                            flush=True,
                        )

                        continue

                    # ----------------------------------------
                    # SAME FORMING CANDLE
                    # ----------------------------------------

                    if (
                        candle_start
                        == live_candle_start
                    ):

                        live_candle_close = (
                            candle_close
                        )

                        continue

                    # ----------------------------------------
                    # NEW CANDLE STARTED
                    #
                    # Therefore previous candle has closed.
                    # ----------------------------------------

                    if (
                        candle_start
                        > live_candle_start
                    ):

                        if (
                            live_candle_close
                            is not None
                        ):

                            await (
                                signal_engine
                                .process_closed_candle(
                                    close_price=(
                                        live_candle_close
                                    ),
                                    candle_time=(
                                        live_candle_start
                                    ),
                                )
                            )

                        live_candle_start = (
                            candle_start
                        )

                        live_candle_close = (
                            candle_close
                        )

                        print(
                            "NEW LIVE 1m CANDLE:",
                            candle_close,
                            flush=True,
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
        f"MODULE {MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "BTCUSDT PENDING SIGNAL "
        "CONFIRMATION ENGINE",
        flush=True,
    )

    print(
        "EMA19 / EMA50 / EMA200",
        flush=True,
    )

    print(
        "CROSSOVER + PENDING CONFIRMATION",
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

    # ----------------------------------------
    # LOAD HISTORICAL DATA
    # ----------------------------------------

    async with aiohttp.ClientSession() as session:

        closes = await load_historical_candles(
            session
        )

    if len(closes) < EMA200_PERIOD:

        print(
            "ERROR: NOT ENOUGH HISTORICAL "
            "CANDLES FOR EMA200",
            flush=True,
        )

        return

    # ----------------------------------------
    # INITIAL EMA ENGINE
    # ----------------------------------------

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

    structure = describe_structure(
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
        "EMA ENGINE READY",
        flush=True,
    )

    # ----------------------------------------
    # TELEGRAM BOT
    # ----------------------------------------

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    # ----------------------------------------
    # STARTUP TELEGRAM VERIFICATION
    # ----------------------------------------

    await send_telegram(
        bot,
        (
            "✅ MODULE 0F-2 ONLINE\n\n"
            "BTCUSDT Pending Signal "
            "Confirmation Engine\n"
            "EMA19 / EMA50 / EMA200\n\n"
            "Live monitoring active."
        ),
    )

    print(
        "========================================",
        flush=True,
    )

    print(
        "LIVE SIGNAL MODE ACTIVE",
        flush=True,
    )

    print(
        "PENDING CONFIRMATION ENGINE ACTIVE",
        flush=True,
    )

    # ----------------------------------------
    # ONE-SHOT SIMULATED TEST
    # ----------------------------------------

    await run_simulated_pending_confirmation_test(
        bot
    )

    print(
        "========================================",
        flush=True,
    )

    # ----------------------------------------
    # START LIVE SIGNAL ENGINE
    # ----------------------------------------

    signal_engine = SignalEngine(
        ema19=ema19,
        ema50=ema50,
        ema200=ema200,
        bot=bot,
    )

    await run_live_engine(
        signal_engine
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
            "MODULE 0F-2 STOPPED",
            flush=True,)
