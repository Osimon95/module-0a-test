import asyncio
import inspect
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

MODULE_NAME = "0F-3"


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
# EMA SETTINGS
# ============================================================

EMA_FAST_PERIOD = 19
EMA_MID_PERIOD = 50
EMA_SLOW_PERIOD = 200


# ============================================================
# 0F-3 SIGNAL QUALITY SETTINGS
# ============================================================

# Minimum EMA19 / EMA50 separation after confirmation.
#
# 0.005 means 0.005%
#
# At BTC = $65,000:
# 0.005% is approximately $3.25.
#
# This helps reject extremely weak EMA crosses.

MIN_EMA_SEPARATION_PERCENT = Decimal(
    os.getenv(
        "MIN_EMA_SEPARATION_PERCENT",
        "0.005",
    )
)


# Require confirmation price to remain on the correct
# side of EMA19.
#
# LONG:
# price > EMA19
#
# SHORT:
# price < EMA19

REQUIRE_PRICE_CONFIRMATION = (
    os.getenv(
        "REQUIRE_PRICE_CONFIRMATION",
        "true",
    ).strip().lower()
    in ("1", "true", "yes", "on")
)


# Require EMA19 to continue moving in the direction of
# the crossover on the confirmation candle.

REQUIRE_EMA19_MOMENTUM = (
    os.getenv(
        "REQUIRE_EMA19_MOMENTUM",
        "true",
    ).strip().lower()
    in ("1", "true", "yes", "on")
)


# Rejected signals are printed to Render logs.
#
# Set this to true if you also want rejected signals
# sent to Telegram.

TELEGRAM_REJECTED_SIGNALS = (
    os.getenv(
        "TELEGRAM_REJECTED_SIGNALS",
        "false",
    ).strip().lower()
    in ("1", "true", "yes", "on")
)


# ============================================================
# SIMULATION
# ============================================================

# Keep disabled for live trading-signal monitoring.

RUN_SIMULATED_QUALITY_TEST_ENABLED = False


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
            "TELEGRAM ERROR:",
            f"{type(error).__name__}: {error}",
            flush=True,
        )


# ============================================================
# DECIMAL HELPERS
# ============================================================

def to_decimal(
    value: Any,
) -> Optional[Decimal]:

    try:

        if value is None:
            return None

        result = Decimal(
            str(value)
        )

        if result <= 0:
            return None

        return result

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return None


def format_decimal(
    value: Decimal,
    places: int = 2,
) -> str:

    return f"{value:.{places}f}"


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


def calculate_all_emas(
    prices: list[Decimal],
) -> tuple[
    Optional[Decimal],
    Optional[Decimal],
    Optional[Decimal],
]:

    ema19 = calculate_ema(
        prices,
        EMA_FAST_PERIOD,
    )

    ema50 = calculate_ema(
        prices,
        EMA_MID_PERIOD,
    )

    ema200 = calculate_ema(
        prices,
        EMA_SLOW_PERIOD,
    )

    return (
        ema19,
        ema50,
        ema200,
    )


# ============================================================
# MARKET STRUCTURE
# ============================================================

def describe_structure(
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> str:

    if (
        ema19
        > ema50
        > ema200
    ):

        return (
            "🟢 STRONG BULLISH "
            "EMA19 > EMA50 > EMA200"
        )

    if (
        ema19
        < ema50
        < ema200
    ):

        return (
            "🔴 STRONG BEARISH "
            "EMA19 < EMA50 < EMA200"
        )

    if (
        ema19 > ema50
        and ema19 > ema200
    ):

        return (
            "🟡 EARLY BULLISH / "
            "RECOVERY STRUCTURE"
        )

    if (
        ema19 < ema50
        and ema19 < ema200
    ):

        return (
            "🟡 EARLY BEARISH / "
            "WEAKENING STRUCTURE"
        )

    return (
        "⚪ MIXED EMA STRUCTURE"
    )


# ============================================================
# HISTORICAL CANDLE EXTRACTION
# ============================================================

def find_historical_list(
    payload: Any,
) -> list[Any]:

    if isinstance(payload, list):

        return payload

    if not isinstance(payload, dict):

        return []

    possible_keys = (
        "data",
        "result",
        "rows",
        "list",
        "candles",
    )

    for key in possible_keys:

        value = payload.get(key)

        if isinstance(value, list):

            return value

        if isinstance(value, dict):

            nested = find_historical_list(
                value
            )

            if nested:
                return nested

    for value in payload.values():

        if isinstance(
            value,
            (dict, list),
        ):

            nested = find_historical_list(
                value
            )

            if nested:
                return nested

    return []


def extract_historical_close(
    candle: Any,
) -> Optional[Decimal]:

    if isinstance(candle, dict):

        possible_keys = (
            "close",
            "c",
            "closePrice",
            "lastPrice",
            "price",
        )

        for key in possible_keys:

            if key in candle:

                value = to_decimal(
                    candle.get(key)
                )

                if value is not None:
                    return value

        return None

    if isinstance(candle, list):

        # Standard kline structure:
        #
        # [
        #   timestamp,
        #   open,
        #   high,
        #   low,
        #   close,
        #   ...
        # ]

        if len(candle) >= 5:

            return to_decimal(
                candle[4]
            )

    return None


# ============================================================
# LOAD HISTORICAL CANDLES
# ============================================================

async def load_historical_closes() -> list[Decimal]:

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
            "granularity": "1m",
            "limit": HISTORICAL_LIMIT,
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
                        "HISTORICAL HTTP STATUS:",
                        response.status,
                        flush=True,
                    )

                    if response.status != 200:
                        continue

                    payload = (
                        await response.json(
                            content_type=None
                        )
                    )

                    raw_candles = (
                        find_historical_list(
                            payload
                        )
                    )

                    closes = []

                    for candle in raw_candles:

                        close = (
                            extract_historical_close(
                                candle
                            )
                        )

                        if close is not None:

                            closes.append(
                                close
                            )

                    # Some APIs return newest first.
                    #
                    # EMA requires oldest -> newest.
                    #
                    # If timestamps aren't available,
                    # the WEEX endpoint normally supplies
                    # chronological klines. We keep the
                    # returned order here.

                    if (
                        len(closes)
                        >= EMA_SLOW_PERIOD
                    ):

                        if len(closes) > HISTORICAL_LIMIT:

                            closes = (
                                closes[
                                    -HISTORICAL_LIMIT:
                                ]
                            )

                        print(
                            "HISTORICAL CANDLES LOADED:",
                            len(closes),
                            flush=True,
                        )

                        print(
                            "LATEST CLOSED PRICE:",
                            closes[-1],
                            flush=True,
                        )

                        return closes

            except Exception as error:

                print(
                    "HISTORICAL ERROR:",
                    f"{type(error).__name__}: "
                    f"{error}",
                    flush=True,
                )

    return []


# ============================================================
# LIVE KLINE EXTRACTION
# ============================================================

def find_kline_object(
    payload: Any,
) -> Optional[Any]:

    if isinstance(payload, dict):

        has_price = any(
            key in payload
            for key in (
                "close",
                "c",
                "closePrice",
                "lastPrice",
            )
        )

        if has_price:
            return payload

        for key in (
            "data",
            "result",
            "kline",
            "candle",
        ):

            if key in payload:

                found = find_kline_object(
                    payload[key]
                )

                if found is not None:
                    return found

        for value in payload.values():

            if isinstance(
                value,
                (dict, list),
            ):

                found = find_kline_object(
                    value
                )

                if found is not None:
                    return found

    if isinstance(payload, list):

        # Possible raw kline array.

        if (
            len(payload) >= 5
            and not isinstance(
                payload[0],
                (dict, list),
            )
        ):

            return payload

        for item in payload:

            found = find_kline_object(
                item
            )

            if found is not None:
                return found

    return None


def extract_live_candle(
    payload: Any,
) -> Optional[dict]:

    candle = find_kline_object(
        payload
    )

    if candle is None:
        return None

    timestamp = None
    open_price = None
    close_price = None

    if isinstance(candle, dict):

        for key in (
            "startTime",
            "start",
            "timestamp",
            "ts",
            "time",
            "t",
        ):

            if key in candle:

                try:

                    timestamp = int(
                        candle[key]
                    )

                    break

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        for key in (
            "open",
            "o",
            "openPrice",
        ):

            if key in candle:

                open_price = to_decimal(
                    candle[key]
                )

                if open_price is not None:
                    break

        for key in (
            "close",
            "c",
            "closePrice",
            "lastPrice",
        ):

            if key in candle:

                close_price = to_decimal(
                    candle[key]
                )

                if close_price is not None:
                    break

    elif isinstance(candle, list):

        if len(candle) >= 5:

            try:

                timestamp = int(
                    candle[0]
                )

            except (
                TypeError,
                ValueError,
            ):

                timestamp = None

            open_price = to_decimal(
                candle[1]
            )

            close_price = to_decimal(
                candle[4]
            )

    if close_price is None:
        return None

    # Fallback if WEEX does not supply kline timestamp.
    # Group messages by the local UTC minute.

    if timestamp is None:

        timestamp = (
            int(time.time())
            // 60
            * 60
        )

    # Normalize millisecond timestamps.

    if timestamp > 10_000_000_000:

        timestamp = (
            timestamp // 1000
        )

    # Normalize to minute bucket.

    timestamp = (
        timestamp
        // 60
        * 60
    )

    if open_price is None:
        open_price = close_price

    return {
        "timestamp": timestamp,
        "open": open_price,
        "close": close_price,
    }


# ============================================================
# SIGNAL QUALITY
# ============================================================

def ema_separation_percent(
    ema19: Decimal,
    ema50: Decimal,
) -> Decimal:

    if ema50 == 0:
        return Decimal("0")

    return (
        abs(
            ema19 - ema50
        )
        / ema50
        * Decimal("100")
    )


def evaluate_signal_quality(
    direction: str,
    price: Decimal,
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
    crossover_ema19: Decimal,
) -> dict:

    separation = (
        ema_separation_percent(
            ema19,
            ema50,
        )
    )

    if direction == "LONG":

        alignment_pass = (
            ema19
            > ema50
            > ema200
        )

        price_pass = (
            price > ema19
        )

        momentum_pass = (
            ema19
            > crossover_ema19
        )

    else:

        alignment_pass = (
            ema19
            < ema50
            < ema200
        )

        price_pass = (
            price < ema19
        )

        momentum_pass = (
            ema19
            < crossover_ema19
        )

    separation_pass = (
        separation
        >= MIN_EMA_SEPARATION_PERCENT
    )

    if not REQUIRE_PRICE_CONFIRMATION:

        price_pass = True

    if not REQUIRE_EMA19_MOMENTUM:

        momentum_pass = True

    passed = all(
        (
            alignment_pass,
            separation_pass,
            price_pass,
            momentum_pass,
        )
    )

    return {
        "passed": passed,
        "alignment": alignment_pass,
        "separation": separation_pass,
        "price": price_pass,
        "momentum": momentum_pass,
        "separation_percent": separation,
    }


# ============================================================
# QUALITY DISPLAY
# ============================================================

def pass_icon(
    passed: bool,
) -> str:

    return (
        "✅"
        if passed
        else "❌"
    )


def quality_log(
    result: dict,
) -> None:

    print(
        "0F-3 SIGNAL QUALITY FILTER",
        flush=True,
    )

    print(
        f"{pass_icon(result['alignment'])} "
        f"FULL EMA ALIGNMENT",
        flush=True,
    )

    print(
        f"{pass_icon(result['separation'])} "
        f"EMA19/EMA50 SEPARATION "
        f"{result['separation_percent']:.6f}% "
        f"(MIN {MIN_EMA_SEPARATION_PERCENT}%)",
        flush=True,
    )

    print(
        f"{pass_icon(result['price'])} "
        f"PRICE CONFIRMATION",
        flush=True,
    )

    print(
        f"{pass_icon(result['momentum'])} "
        f"EMA19 MOMENTUM",
        flush=True,
    )


# ============================================================
# SIGNAL ENGINE
# ============================================================

class SignalEngine:

    def __init__(
        self,
        historical_closes: list[Decimal],
        bot: Bot,
    ):

        self.closes = list(
            historical_closes
        )

        self.bot = bot

        (
            self.previous_ema19,
            self.previous_ema50,
            self.previous_ema200,
        ) = calculate_all_emas(
            self.closes
        )

        self.pending_signal = None

    async def process_closed_candle(
        self,
        candle: dict,
    ) -> None:

        close_price = candle["close"]

        self.closes.append(
            close_price
        )

        # Keep enough history for stable EMA calculation.

        if len(self.closes) > 500:

            self.closes = (
                self.closes[-500:]
            )

        (
            ema19,
            ema50,
            ema200,
        ) = calculate_all_emas(
            self.closes
        )

        if (
            ema19 is None
            or ema50 is None
            or ema200 is None
        ):

            print(
                "EMA ERROR: INSUFFICIENT DATA",
                flush=True,
            )

            return

        print(
            "=" * 40,
            flush=True,
        )

        print(
            f"MODULE {MODULE_NAME} - "
            f"CLOSED 1m CANDLE",
            flush=True,
        )

        print(
            f"{SYMBOL} CLOSE: "
            f"{close_price}",
            flush=True,
        )

        print(
            "EMA19:",
            format_decimal(ema19),
            flush=True,
        )

        print(
            "EMA50:",
            format_decimal(ema50),
            flush=True,
        )

        print(
            "EMA200:",
            format_decimal(ema200),
            flush=True,
        )

        print(
            "STRUCTURE:",
            describe_structure(
                ema19,
                ema50,
                ema200,
            ),
            flush=True,
        )

        # ====================================================
        # FIRST:
        # CHECK EXISTING PENDING SIGNAL
        # ====================================================

        if self.pending_signal is not None:

            await self.confirm_pending_signal(
                close_price=close_price,
                ema19=ema19,
                ema50=ema50,
                ema200=ema200,
            )

        # ====================================================
        # SECOND:
        # DETECT NEW CROSSOVER
        # ====================================================

        bullish_cross = (
            self.previous_ema19
            is not None
            and self.previous_ema50
            is not None
            and self.previous_ema19
            <= self.previous_ema50
            and ema19
            > ema50
        )

        bearish_cross = (
            self.previous_ema19
            is not None
            and self.previous_ema50
            is not None
            and self.previous_ema19
            >= self.previous_ema50
            and ema19
            < ema50
        )

        if (
            self.pending_signal is None
            and bullish_cross
        ):

            await self.start_pending_signal(
                direction="LONG",
                price=close_price,
                ema19=ema19,
                ema50=ema50,
                ema200=ema200,
            )

        elif (
            self.pending_signal is None
            and bearish_cross
        ):

            await self.start_pending_signal(
                direction="SHORT",
                price=close_price,
                ema19=ema19,
                ema50=ema50,
                ema200=ema200,
            )

        self.previous_ema19 = ema19
        self.previous_ema50 = ema50
        self.previous_ema200 = ema200

    async def start_pending_signal(
        self,
        direction: str,
        price: Decimal,
        ema19: Decimal,
        ema50: Decimal,
        ema200: Decimal,
    ) -> None:

        self.pending_signal = {
            "direction": direction,
            "price": price,
            "ema19": ema19,
            "ema50": ema50,
            "ema200": ema200,
        }

        print(
            "=" * 40,
            flush=True,
        )

        if direction == "LONG":

            print(
                "BULLISH CROSSOVER DETECTED",
                flush=True,
            )

            print(
                "EMA19 CROSSED ABOVE EMA50",
                flush=True,
            )

        else:

            print(
                "BEARISH CROSSOVER DETECTED",
                flush=True,
            )

            print(
                "EMA19 CROSSED BELOW EMA50",
                flush=True,
            )

        print(
            "SIGNAL ENTERED PENDING STATE",
            flush=True,
        )

        print(
            "WAITING FOR NEXT CLOSED "
            "1m CANDLE + 0F-3 QUALITY FILTER",
            flush=True,
        )

    async def confirm_pending_signal(
        self,
        close_price: Decimal,
        ema19: Decimal,
        ema50: Decimal,
        ema200: Decimal,
    ) -> None:

        pending = self.pending_signal

        if pending is None:
            return

        direction = pending[
            "direction"
        ]

        print(
            "=" * 40,
            flush=True,
        )

        print(
            f"PENDING {direction} "
            f"SIGNAL CONFIRMATION",
            flush=True,
        )

        result = (
            evaluate_signal_quality(
                direction=direction,
                price=close_price,
                ema19=ema19,
                ema50=ema50,
                ema200=ema200,
                crossover_ema19=(
                    pending["ema19"]
                ),
            )
        )

        quality_log(
            result
        )

        # Clear old pending state before
        # sending or rejecting.

        self.pending_signal = None

        if result["passed"]:

            print(
                "0F-3 SIGNAL QUALITY: PASSED",
                flush=True,
            )

            await self.send_confirmed_signal(
                direction=direction,
                price=close_price,
                ema19=ema19,
                ema50=ema50,
                ema200=ema200,
                quality=result,
            )

        else:

            print(
                "0F-3 SIGNAL QUALITY: REJECTED",
                flush=True,
            )

            print(
                "NO TRADE SIGNAL SENT",
                flush=True,
            )

            if TELEGRAM_REJECTED_SIGNALS:

                message = (
                    f"⚠️ {SYMBOL} {direction} "
                    f"SIGNAL REJECTED\n\n"
                    f"EMA crossover detected\n"
                    f"Next 1m candle checked\n\n"
                    f"{pass_icon(result['alignment'])} "
                    f"EMA alignment\n"
                    f"{pass_icon(result['separation'])} "
                    f"EMA separation\n"
                    f"{pass_icon(result['price'])} "
                    f"Price confirmation\n"
                    f"{pass_icon(result['momentum'])} "
                    f"EMA19 momentum\n\n"
                    f"MODULE {MODULE_NAME}"
                )

                await send_telegram(
                    self.bot,
                    message,
                )

    async def send_confirmed_signal(
        self,
        direction: str,
        price: Decimal,
        ema19: Decimal,
        ema50: Decimal,
        ema200: Decimal,
        quality: dict,
    ) -> None:

        if direction == "LONG":

            icon = "🟢"

            crossover_text = (
                "EMA19 / EMA50 "
                "BULLISH CROSSOVER"
            )

            structure_text = (
                "EMA19 > EMA50 > EMA200"
            )

        else:

            icon = "🔴"

            crossover_text = (
                "EMA19 / EMA50 "
                "BEARISH CROSSOVER"
            )

            structure_text = (
                "EMA19 < EMA50 < EMA200"
            )

        message = (
            f"{icon} {SYMBOL} "
            f"{direction} SIGNAL\n\n"
            f"✅ {crossover_text}\n"
            f"✅ NEXT 1m CANDLE CONFIRMED\n"
            f"✅ 0F-3 QUALITY FILTER PASSED\n"
            f"✅ {structure_text}\n\n"
            f"Price: {price}\n"
            f"EMA19: {format_decimal(ema19)}\n"
            f"EMA50: {format_decimal(ema50)}\n"
            f"EMA200: {format_decimal(ema200)}\n"
            f"EMA19/50 separation: "
            f"{quality['separation_percent']:.6f}%\n\n"
            f"MODULE {MODULE_NAME}"
        )

        await send_telegram(
            self.bot,
            message,
        )

        print(
            f"{direction} SIGNAL CONFIRMED",
            flush=True,
        )


# ============================================================
# WEBSOCKET PING HANDLING
# ============================================================

async def handle_application_ping(
    websocket: Any,
    payload: Any,
) -> bool:

    if isinstance(payload, dict):

        if "ping" in payload:

            pong_payload = {
                "pong": payload["ping"]
            }

            await websocket.send(
                json.dumps(
                    pong_payload
                )
            )

            print(
                "APPLICATION PONG SENT",
                flush=True,
            )

            return True

        event = str(
            payload.get(
                "event",
                ""
            )
        ).lower()

        if event == "ping":

            await websocket.send(
                json.dumps(
                    {
                        "event": "pong"
                    }
                )
            )

            print(
                "APPLICATION PONG SENT",
                flush=True,
            )

            return True

    return False


# ============================================================
# WEBSOCKET CONNECTION HELPER
# ============================================================

def websocket_connect_kwargs() -> dict:

    kwargs = {
        "ping_interval": None,
        "close_timeout": 10,
    }

    try:

        parameters = (
            inspect.signature(
                websockets.connect
            ).parameters
        )

        headers = {
            "User-Agent":
            "WEEX-BTC-Bot/0F-3"
        }

        if (
            "additional_headers"
            in parameters
        ):

            kwargs[
                "additional_headers"
            ] = headers

        elif (
            "extra_headers"
            in parameters
        ):

            kwargs[
                "extra_headers"
            ] = headers

    except Exception:
        pass

    return kwargs


# ============================================================
# LIVE WEBSOCKET LOOP
# ============================================================

async def run_live_engine(
    engine: SignalEngine,
) -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    current_candle = None

    while True:

        try:

            kwargs = (
                websocket_connect_kwargs()
            )

            async with websockets.connect(
                WS_URL,
                **kwargs,
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

                async for raw_message in websocket:

                    try:

                        if isinstance(
                            raw_message,
                            bytes,
                        ):

                            raw_message = (
                                raw_message.decode(
                                    "utf-8"
                                )
                            )

                        payload = json.loads(
                            raw_message
                        )

                    except Exception:

                        continue

                    if await handle_application_ping(
                        websocket,
                        payload,
                    ):

                        continue

                    # Subscription confirmation.

                    if isinstance(
                        payload,
                        dict,
                    ):

                        if (
                            payload.get("id") == 1
                            or str(
                                payload.get(
                                    "event",
                                    ""
                                )
                            ).lower()
                            in (
                                "subscribe",
                                "subscribed",
                            )
                        ):

                            print(
                                "SUBSCRIPTION CONFIRMED",
                                flush=True,
                            )

                    candle = (
                        extract_live_candle(
                            payload
                        )
                    )

                    if candle is None:
                        continue

                    # First observed live candle.

                    if current_candle is None:

                        current_candle = candle

                        print(
                            "LIVE 1m CANDLE STARTED:",
                            current_candle[
                                "close"
                            ],
                            flush=True,
                        )

                        continue

                    # Same 1m candle:
                    # update its current close.

                    if (
                        candle["timestamp"]
                        == current_candle[
                            "timestamp"
                        ]
                    ):

                        current_candle[
                            "close"
                        ] = candle[
                            "close"
                        ]

                        continue

                    # New minute detected.
                    #
                    # Previous candle is now closed.

                    if (
                        candle["timestamp"]
                        > current_candle[
                            "timestamp"
                        ]
                    ):

                        closed_candle = (
                            current_candle
                        )

                        await engine.process_closed_candle(
                            closed_candle
                        )

                        current_candle = (
                            candle
                        )

                        print(
                            "NEW LIVE 1m CANDLE:",
                            current_candle[
                                "close"
                            ],
                            flush=True,
                        )

        except asyncio.CancelledError:

            raise

        except Exception as error:

            print(
                "WEBSOCKET ERROR:",
                f"{type(error).__name__}: "
                f"{error}",
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
# OPTIONAL SIMULATED QUALITY TEST
# ============================================================

async def run_simulated_quality_test(
    bot: Bot,
) -> None:

    print(
        "=" * 40,
        flush=True,
    )

    print(
        "MODULE 0F-3 SIMULATED "
        "QUALITY TEST",
        flush=True,
    )

    result = evaluate_signal_quality(
        direction="LONG",
        price=Decimal("65050"),
        ema19=Decimal("65010"),
        ema50=Decimal("65005"),
        ema200=Decimal("64980"),
        crossover_ema19=Decimal(
            "65000"
        ),
    )

    quality_log(
        result
    )

    print(
        "SIMULATED QUALITY RESULT:",
        (
            "PASSED"
            if result["passed"]
            else "REJECTED"
        ),
        flush=True,
    )

    print(
        "SIMULATED TEST COMPLETE",
        flush=True,
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
        f"MODULE {MODULE_NAME} STARTING",
        flush=True,
    )

    print(
        "BTCUSDT SIGNAL QUALITY "
        "CONFIRMATION ENGINE",
        flush=True,
    )

    print(
        "EMA19 / EMA50 / EMA200",
        flush=True,
    )

    print(
        "CROSSOVER + PENDING CONFIRMATION "
        "+ QUALITY FILTER",
        flush=True,
    )

    print(
        "=" * 40,
        flush=True,
    )

    print(
        "TELEGRAM CONFIG:",
        (
            "READY"
            if telegram_is_configured()
            else "MISSING"
        ),
        flush=True,
    )

    historical_closes = (
        await load_historical_closes()
    )

    if (
        len(historical_closes)
        < EMA_SLOW_PERIOD
    ):

        print(
            "ERROR: NOT ENOUGH "
            "HISTORICAL CANDLES FOR EMA200",
            flush=True,
        )

        return

    (
        ema19,
        ema50,
        ema200,
    ) = calculate_all_emas(
        historical_closes
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

    print(
        "INITIAL EMA ENGINE",
        flush=True,
    )

    print(
        "EMA19:",
        format_decimal(ema19),
        flush=True,
    )

    print(
        "EMA50:",
        format_decimal(ema50),
        flush=True,
    )

    print(
        "EMA200:",
        format_decimal(ema200),
        flush=True,
    )

    print(
        "STRUCTURE:",
        describe_structure(
            ema19,
            ema50,
            ema200,
        ),
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
        "0F-3 QUALITY FILTER SETTINGS",
        flush=True,
    )

    print(
        "MIN EMA19/50 SEPARATION:",
        f"{MIN_EMA_SEPARATION_PERCENT}%",
        flush=True,
    )

    print(
        "PRICE CONFIRMATION:",
        (
            "ENABLED"
            if REQUIRE_PRICE_CONFIRMATION
            else "DISABLED"
        ),
        flush=True,
    )

    print(
        "EMA19 MOMENTUM:",
        (
            "ENABLED"
            if REQUIRE_EMA19_MOMENTUM
            else "DISABLED"
        ),
        flush=True,
    )

    print(
        "=" * 40,
        flush=True,
    )

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )

    await send_telegram(
        bot,
        (
            f"✅ MODULE {MODULE_NAME} ONLINE\n\n"
            f"{SYMBOL} Signal Quality "
            f"Confirmation Engine\n\n"
            f"EMA19 / EMA50 / EMA200\n"
            f"Pending next-candle confirmation\n"
            f"0F-3 quality filtering active.\n\n"
            f"Live monitoring active."
        ),
    )

    engine = SignalEngine(
        historical_closes=(
            historical_closes
        ),
        bot=bot,
    )

    print(
        "LIVE SIGNAL MODE ACTIVE",
        flush=True,
    )

    print(
        "PENDING CONFIRMATION ENGINE ACTIVE",
        flush=True,
    )

    print(
        "0F-3 SIGNAL QUALITY FILTER ACTIVE",
        flush=True,
    )

    if RUN_SIMULATED_QUALITY_TEST_ENABLED:

        print(
            "SIMULATED QUALITY TEST ENABLED",
            flush=True,
        )

        await run_simulated_quality_test(
            bot
        )

    else:

        print(
            "SIMULATED TEST DISABLED",
            flush=True,
        )

    print(
        "=" * 40,
        flush=True,
    )

    await run_live_engine(
        engine
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
