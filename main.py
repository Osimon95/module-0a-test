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

HISTORICAL_LIMIT = 250

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
            "TOKEN OR CHAT ID MISSING",
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
# EMA
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
            price * multiplier
            + ema
            * (
                Decimal("1")
                - multiplier
            )
        )

    return ema


# ============================================================
# STRUCTURE
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
# HISTORICAL CANDLE EXTRACTION
# ============================================================

def extract_historical_data(
    payload: Any,
) -> list:

    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    possible_keys = (
        "data",
        "result",
        "list",
        "rows",
    )

    for key in possible_keys:

        value = payload.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):

            for nested_key in (
                "list",
                "rows",
                "data",
            ):

                nested = value.get(
                    nested_key
                )

                if isinstance(
                    nested,
                    list,
                ):
                    return nested

    return []


def extract_historical_close(
    candle: Any,
) -> Optional[Decimal]:

    if isinstance(candle, dict):

        for key in (
            "close",
            "c",
            "closePrice",
            "lastPrice",
        ):

            price = to_decimal(
                candle.get(key)
            )

            if price is not None:
                return price

    if isinstance(candle, list):

        if len(candle) >= 5:

            price = to_decimal(
                candle[4]
            )

            if price is not None:
                return price

    return None


# ============================================================
# LOAD HISTORICAL CANDLES
# ============================================================

async def load_historical_prices() -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES...",
        flush=True,
    )

    parameters = {
        "symbol": SYMBOL,
        "interval": "1m",
        "limit": HISTORICAL_LIMIT,
    }

    async with aiohttp.ClientSession() as session:

        try:

            async with session.get(
                HISTORICAL_URL,
                params=parameters,
                timeout=20,
            ) as response:

                print(
                    "HISTORICAL HTTP STATUS:",
                    response.status,
                    flush=True,
                )

                if response.status != 200:
                    return []

                payload = await response.json()

        except Exception as error:

            print(
                "HISTORICAL ERROR:",
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )

            return []

    candles = extract_historical_data(
        payload
    )

    prices = []

    for candle in candles:

        close = extract_historical_close(
            candle
        )

        if close is not None:
            prices.append(close)

    print(
        "HISTORICAL CANDLES LOADED: "
        f"{len(prices)}",
        flush=True,
    )

    return prices


# ============================================================
# LIVE KLINE EXTRACTION
# ============================================================

def extract_live_candle(
    message: Any,
) -> Optional[tuple[str, Decimal]]:

    if not isinstance(message, dict):
        return None

    data = message.get("data")

    if data is None:
        return None

    # --------------------------------------------------------
    # DATA AS DICTIONARY
    # --------------------------------------------------------

    if isinstance(data, dict):

        timestamp = (
            data.get("timestamp")
            or data.get("ts")
            or data.get("time")
            or data.get("t")
        )

        close = None

        for key in (
            "close",
            "c",
            "closePrice",
            "lastPrice",
            "price",
        ):

            close = to_decimal(
                data.get(key)
            )

            if close is not None:
                break

        if (
            timestamp is not None
            and close is not None
        ):

            return (
                str(timestamp),
                close,
            )

    # --------------------------------------------------------
    # DATA AS LIST
    # --------------------------------------------------------

    if isinstance(data, list):

        if not data:
            return None

        candle = data[0]

        if isinstance(candle, list):

            if len(candle) >= 5:

                timestamp = candle[0]

                close = to_decimal(
                    candle[4]
                )

                if close is not None:

                    return (
                        str(timestamp),
                        close,
                    )

        if isinstance(candle, dict):

            timestamp = (
                candle.get("timestamp")
                or candle.get("ts")
                or candle.get("time")
                or candle.get("t")
            )

            close = None

            for key in (
                "close",
                "c",
                "closePrice",
                "lastPrice",
                "price",
            ):

                close = to_decimal(
                    candle.get(key)
                )

                if close is not None:
                    break

            if (
                timestamp is not None
                and close is not None
            ):

                return (
                    str(timestamp),
                    close,
                )

    return None


# ============================================================
# SIGNAL ENGINE
# ============================================================

class SignalEngine:

    def __init__(
        self,
        prices: list[Decimal],
    ) -> None:

        self.prices = prices[-500:]

        self.previous_ema19 = calculate_ema(
            self.prices,
            19,
        )

        self.previous_ema50 = calculate_ema(
            self.prices,
            50,
        )

        self.previous_ema200 = calculate_ema(
            self.prices,
            200,
        )

        # ----------------------------------------------------
        # LAST SUCCESSFULLY SENT SIGNAL
        # ----------------------------------------------------

        self.last_signal: Optional[str] = None

        # ----------------------------------------------------
        # PENDING SIGNAL
        #
        # LONG:
        # EMA19 crossed above EMA50 but price
        # has not yet confirmed above EMA200.
        #
        # SHORT:
        # EMA19 crossed below EMA50 but price
        # has not yet confirmed below EMA200.
        # ----------------------------------------------------

        self.pending_signal: Optional[str] = None

        # ----------------------------------------------------
        # INITIAL RELATIONSHIP
        # ----------------------------------------------------

        if (
            self.previous_ema19 is not None
            and self.previous_ema50 is not None
        ):

            if (
                self.previous_ema19
                > self.previous_ema50
            ):

                self.last_relationship = "ABOVE"

            elif (
                self.previous_ema19
                < self.previous_ema50
            ):

                self.last_relationship = "BELOW"

            else:

                self.last_relationship = "EQUAL"

        else:

            self.last_relationship = None


    # ========================================================
    # SEND LONG
    # ========================================================

    async def send_long_signal(
        self,
        bot: Bot,
        close: Decimal,
        ema19: Decimal,
        ema50: Decimal,
        ema200: Decimal,
        structure: str,
        confirmation_type: str,
    ) -> None:

        if self.last_signal == "LONG":

            print(
                "DUPLICATE LONG SIGNAL BLOCKED",
                flush=True,
            )

            return

        message = (
            "🟢 BTCUSDT LONG SIGNAL\n\n"
            "EMA19 ABOVE EMA50\n\n"
            f"PRICE: {close}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            f"{structure}\n\n"
            "✅ CONFIRMATION:\n"
            "Price is ABOVE EMA200\n\n"
            f"{confirmation_type}\n\n"
            "MODULE 0F-2"
        )

        await send_telegram(
            bot,
            message,
        )

        self.last_signal = "LONG"

        self.pending_signal = None


    # ========================================================
    # SEND SHORT
    # ========================================================

    async def send_short_signal(
        self,
        bot: Bot,
        close: Decimal,
        ema19: Decimal,
        ema50: Decimal,
        ema200: Decimal,
        structure: str,
        confirmation_type: str,
    ) -> None:

        if self.last_signal == "SHORT":

            print(
                "DUPLICATE SHORT SIGNAL BLOCKED",
                flush=True,
            )

            return

        message = (
            "🔴 BTCUSDT SHORT SIGNAL\n\n"
            "EMA19 BELOW EMA50\n\n"
            f"PRICE: {close}\n"
            f"EMA19: {ema19:.2f}\n"
            f"EMA50: {ema50:.2f}\n"
            f"EMA200: {ema200:.2f}\n\n"
            f"{structure}\n\n"
            "✅ CONFIRMATION:\n"
            "Price is BELOW EMA200\n\n"
            f"{confirmation_type}\n\n"
            "MODULE 0F-2"
        )

        await send_telegram(
            bot,
            message,
        )

        self.last_signal = "SHORT"

        self.pending_signal = None


    # ========================================================
    # PROCESS CLOSED CANDLE
    # ========================================================

    async def process_closed_candle(
        self,
        bot: Bot,
        close: Decimal,
    ) -> None:

        self.prices.append(close)

        self.prices = self.prices[-500:]

        ema19 = calculate_ema(
            self.prices,
            19,
        )

        ema50 = calculate_ema(
            self.prices,
            50,
        )

        ema200 = calculate_ema(
            self.prices,
            200,
        )

        if (
            ema19 is None
            or ema50 is None
            or ema200 is None
        ):
            return

        print(
            "=" * 40,
            flush=True,
        )

        print(
            "MODULE 0F-2 - "
            "CLOSED 1m CANDLE",
            flush=True,
        )

        print(
            f"{SYMBOL} CLOSE: {close}",
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

        # ----------------------------------------------------
        # CURRENT EMA19 / EMA50 RELATIONSHIP
        # ----------------------------------------------------

        if ema19 > ema50:

            current_relationship = "ABOVE"

        elif ema19 < ema50:

            current_relationship = "BELOW"

        else:

            current_relationship = "EQUAL"

        # ----------------------------------------------------
        # CROSSOVER DETECTION
        # ----------------------------------------------------

        bullish_cross = (
            self.last_relationship
            in (
                "BELOW",
                "EQUAL",
            )
            and
            current_relationship == "ABOVE"
        )

        bearish_cross = (
            self.last_relationship
            in (
                "ABOVE",
                "EQUAL",
            )
            and
            current_relationship == "BELOW"
        )

        # ====================================================
        # BULLISH CROSSOVER
        # ====================================================

        if bullish_cross:

            print(
                "REAL BULLISH CROSSOVER "
                "DETECTED",
                flush=True,
            )

            # A complete bearish-to-bullish cycle
            # re-arms the LONG signal.

            if self.last_signal == "LONG":

                self.last_signal = None

                print(
                    "LONG SIGNAL RE-ARMED",
                    flush=True,
                )

            # Cancel any old SHORT waiting for
            # confirmation.

            if self.pending_signal == "SHORT":

                print(
                    "PENDING SHORT CANCELLED",
                    flush=True,
                )

                self.pending_signal = None

            # Immediate confirmation.

            if close > ema200:

                print(
                    "BULLISH CROSS "
                    "IMMEDIATELY CONFIRMED",
                    flush=True,
                )

                await self.send_long_signal(
                    bot,
                    close,
                    ema19,
                    ema50,
                    ema200,
                    structure,
                    "⚡ CROSSOVER CONFIRMED "
                    "IMMEDIATELY",
                )

            else:

                self.pending_signal = "LONG"

                print(
                    "PENDING LONG CREATED",
                    flush=True,
                )

                print(
                    "WAITING FOR PRICE "
                    "ABOVE EMA200",
                    flush=True,
                )

        # ====================================================
        # BEARISH CROSSOVER
        # ====================================================

        if bearish_cross:

            print(
                "REAL BEARISH CROSSOVER "
                "DETECTED",
                flush=True,
            )

            # A complete bullish-to-bearish cycle
            # re-arms the SHORT signal.

            if self.last_signal == "SHORT":

                self.last_signal = None

                print(
                    "SHORT SIGNAL RE-ARMED",
                    flush=True,
                )

            # Cancel any old LONG waiting for
            # confirmation.

            if self.pending_signal == "LONG":

                print(
                    "PENDING LONG CANCELLED",
                    flush=True,
                )

                self.pending_signal = None

            # Immediate confirmation.

            if close < ema200:

                print(
                    "BEARISH CROSS "
                    "IMMEDIATELY CONFIRMED",
                    flush=True,
                )

                await self.send_short_signal(
                    bot,
                    close,
                    ema19,
                    ema50,
                    ema200,
                    structure,
                    "⚡ CROSSOVER CONFIRMED "
                    "IMMEDIATELY",
                )

            else:

                self.pending_signal = "SHORT"

                print(
                    "PENDING SHORT CREATED",
                    flush=True,
                )

                print(
                    "WAITING FOR PRICE "
                    "BELOW EMA200",
                    flush=True,
                )

        # ====================================================
        # PENDING LONG ENGINE
        # ====================================================

        if self.pending_signal == "LONG":

            # Bullish EMA relationship disappeared.
            # Pending LONG is no longer valid.

            if ema19 <= ema50:

                print(
                    "PENDING LONG INVALIDATED",
                    flush=True,
                )

                print(
                    "EMA19 NO LONGER "
                    "ABOVE EMA50",
                    flush=True,
                )

                self.pending_signal = None

            # Bullish relationship remains valid
            # and price finally confirms.

            elif close > ema200:

                print(
                    "PENDING LONG CONFIRMED",
                    flush=True,
                )

                print(
                    "PRICE MOVED ABOVE EMA200",
                    flush=True,
                )

                await self.send_long_signal(
                    bot,
                    close,
                    ema19,
                    ema50,
                    ema200,
                    structure,
                    "⏳ DELAYED EMA200 "
                    "CONFIRMATION",
                )

            else:

                print(
                    "PENDING LONG ACTIVE",
                    flush=True,
                )

                print(
                    "PRICE STILL BELOW EMA200",
                    flush=True,
                )

        # ====================================================
        # PENDING SHORT ENGINE
        # ====================================================

        if self.pending_signal == "SHORT":

            # Bearish EMA relationship disappeared.
            # Pending SHORT is no longer valid.

            if ema19 >= ema50:

                print(
                    "PENDING SHORT INVALIDATED",
                    flush=True,
                )

                print(
                    "EMA19 NO LONGER "
                    "BELOW EMA50",
                    flush=True,
                )

                self.pending_signal = None

            # Bearish relationship remains valid
            # and price finally confirms.

            elif close < ema200:

                print(
                    "PENDING SHORT CONFIRMED",
                    flush=True,
                )

                print(
                    "PRICE MOVED BELOW EMA200",
                    flush=True,
                )

                await self.send_short_signal(
                    bot,
                    close,
                    ema19,
                    ema50,
                    ema200,
                    structure,
                    "⏳ DELAYED EMA200 "
                    "CONFIRMATION",
                )

            else:

                print(
                    "PENDING SHORT ACTIVE",
                    flush=True,
                )

                print(
                    "PRICE STILL ABOVE EMA200",
                    flush=True,
                )

        # ----------------------------------------------------
        # PENDING STATUS
        # ----------------------------------------------------

        if self.pending_signal is None:

            print(
                "PENDING SIGNAL: NONE",
                flush=True,
            )

        else:

            print(
                "PENDING SIGNAL: "
                f"{self.pending_signal}",
                flush=True,
            )

        # ----------------------------------------------------
        # UPDATE ENGINE STATE
        # ----------------------------------------------------

        self.last_relationship = (
            current_relationship
        )

        self.previous_ema19 = ema19
        self.previous_ema50 = ema50
        self.previous_ema200 = ema200


# ============================================================
# WEBSOCKET ENGINE
# ============================================================

async def run_websocket(
    bot: Bot,
    signal_engine: SignalEngine,
) -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    current_candle_time = None
    current_candle_close = None

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
                    # SUBSCRIPTION CONFIRMATION
                    # ----------------------------------------

                    if isinstance(
                        message,
                        dict,
                    ):

                        if (
                            message.get("id")
                            == 1
                        ):

                            print(
                                "SUBSCRIPTION "
                                "CONFIRMED",
                                flush=True,
                            )

                            continue

                    # ----------------------------------------
                    # APPLICATION PING / PONG
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

                            pong_message = {
                                "event": "pong"
                            }

                            await websocket.send(
                                json.dumps(
                                    pong_message
                                )
                            )

                            print(
                                "APPLICATION "
                                "PONG SENT",
                                flush=True,
                            )

                            continue

                    # ----------------------------------------
                    # LIVE CANDLE
                    # ----------------------------------------

                    candle = extract_live_candle(
                        message
                    )

                    if candle is None:
                        continue

                    candle_time, close = candle

                    # First candle received.

                    if (
                        current_candle_time
                        is None
                    ):

                        current_candle_time = (
                            candle_time
                        )

                        current_candle_close = (
                            close
                        )

                        print(
                            "LIVE 1m CANDLE "
                            f"STARTED: {close}",
                            flush=True,
                        )

                        continue

                    # Same candle still updating.

                    if (
                        candle_time
                        == current_candle_time
                    ):

                        current_candle_close = (
                            close
                        )

                        continue

                    # ----------------------------------------
                    # NEW CANDLE =
                    # PREVIOUS CANDLE CLOSED
                    # ----------------------------------------

                    if (
                        current_candle_close
                        is not None
                    ):

                        await (
                            signal_engine
                            .process_closed_candle(
                                bot,
                                current_candle_close,
                            )
                        )

                    current_candle_time = (
                        candle_time
                    )

                    current_candle_close = (
                        close
                    )

                    print(
                        "NEW LIVE 1m CANDLE: "
                        f"{close}",
                        flush=True,
                    )

        except Exception as error:

            print(
                "WEBSOCKET ERROR:",
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )

            print(
                "RECONNECTING IN "
                f"{reconnect_delay} "
                "SECONDS...",
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
        "=" * 40,
        flush=True,
    )

    print(
        "MODULE 0F-2 STARTING",
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
        "CROSSOVER + PENDING "
        "CONFIRMATION",
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

    prices = (
        await load_historical_prices()
    )

    if len(prices) < 200:

        print(
            "ERROR: NOT ENOUGH "
            "HISTORICAL CANDLES "
            "FOR EMA200",
            flush=True,
        )

        return

    print(
        "LATEST CLOSED PRICE: "
        f"{prices[-1]}",
        flush=True,
    )

    signal_engine = SignalEngine(
        prices
    )

    ema19 = (
        signal_engine.previous_ema19
    )

    ema50 = (
        signal_engine.previous_ema50
    )

    ema200 = (
        signal_engine.previous_ema200
    )

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):

        print(
            "ERROR INITIALIZING "
            "EMA ENGINE",
            flush=True,
        )

        return

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

    print(
        "=" * 40,
        flush=True,
    )

    print(
        "LIVE SIGNAL MODE ACTIVE",
        flush=True,
    )

    print(
        "PENDING CONFIRMATION "
        "ENGINE ACTIVE",
        flush=True,
    )

    print(
        "SIMULATED TEST DISABLED",
        flush=True,
    )

    print(
        "=" * 40,
        flush=True,
    )

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    await run_websocket(
        bot,
        signal_engine,
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "MODULE 0F-2 STOPPED",
            flush=True,)
