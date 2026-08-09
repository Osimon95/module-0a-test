import asyncio
import json
import os
from collections import deque
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4A"


# ============================================================
# CORE MARKET CONFIGURATION
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

HISTORICAL_INTERVAL = "1m"
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


# ============================================================
# HELPERS FOR ENVIRONMENT VARIABLES
# ============================================================

def env_decimal(
    name: str,
    default: str,
) -> Decimal:

    value = os.getenv(name, default).strip()

    try:
        return Decimal(value)

    except InvalidOperation:
        return Decimal(default)


def env_int(
    name: str,
    default: int,
) -> int:

    value = os.getenv(
        name,
        str(default),
    ).strip()

    try:
        return int(value)

    except ValueError:
        return default


def env_bool(
    name: str,
    default: bool,
) -> bool:

    default_text = (
        "true"
        if default
        else "false"
    )

    value = os.getenv(
        name,
        default_text,
    ).strip().lower()

    return value in {
        "1",
        "true",
        "yes",
        "on",
    }


# ============================================================
# TRADE CONFIGURATION
#
# ALL VALUES CAN LATER BE CHANGED FROM RENDER ENVIRONMENT
# WITHOUT EDITING main.py
# ============================================================

INITIAL_POSITION_PERCENT = env_decimal(
    "INITIAL_POSITION_PERCENT",
    "5",
)

LEVERAGE = env_decimal(
    "LEVERAGE",
    "5",
)

MAX_LEVERAGE = env_decimal(
    "MAX_LEVERAGE",
    "10",
)


# ============================================================
# PYRAMID CONFIGURATION
#
# MAX_PYRAMID_ADDS CAN BE CHANGED LATER WITHOUT CODE EDIT
# ============================================================

MAX_PYRAMID_ADDS = env_int(
    "MAX_PYRAMID_ADDS",
    1,
)

PYRAMID_1_PERCENT = env_decimal(
    "PYRAMID_1_PERCENT",
    "5",
)

PYRAMID_2_PERCENT = env_decimal(
    "PYRAMID_2_PERCENT",
    "5",
)

PYRAMID_3_PERCENT = env_decimal(
    "PYRAMID_3_PERCENT",
    "5",
)


# ============================================================
# BACKUP CONFIGURATION
# ============================================================

MAX_BACKUPS = env_int(
    "MAX_BACKUPS",
    3,
)

BACKUP_1_PERCENT = env_decimal(
    "BACKUP_1_PERCENT",
    "5",
)

BACKUP_2_PERCENT = env_decimal(
    "BACKUP_2_PERCENT",
    "5",
)

BACKUP_3_PERCENT = env_decimal(
    "BACKUP_3_PERCENT",
    "5",
)


# ============================================================
# LIQUIDATION SAFETY CONFIGURATION
#
# BACKUPS ARE NOT PLACED BY THIS MODULE.
# THESE SETTINGS PREPARE THE SAFETY LAYER ONLY.
# ============================================================

LIQUIDATION_SAFETY_BUFFER_PERCENT = env_decimal(
    "LIQUIDATION_SAFETY_BUFFER_PERCENT",
    "0.50",
)

MIN_LIQUIDATION_DISTANCE_PERCENT = env_decimal(
    "MIN_LIQUIDATION_DISTANCE_PERCENT",
    "1.00",
)


# ============================================================
# TAKE PROFIT CONFIGURATION
#
# TP1 = 20%
# TP2 = 20%
# TP3 = remaining 60%, intended for trailing profit
# ============================================================

TP1_POSITION_PERCENT = env_decimal(
    "TP1_POSITION_PERCENT",
    "20",
)

TP2_POSITION_PERCENT = env_decimal(
    "TP2_POSITION_PERCENT",
    "20",
)

TP3_POSITION_PERCENT = env_decimal(
    "TP3_POSITION_PERCENT",
    "60",
)

TP1_TARGET_PERCENT = env_decimal(
    "TP1_TARGET_PERCENT",
    "0.30",
)

TP2_TARGET_PERCENT = env_decimal(
    "TP2_TARGET_PERCENT",
    "0.60",
)

TRAILING_ACTIVATION_PERCENT = env_decimal(
    "TRAILING_ACTIVATION_PERCENT",
    "0.80",
)

TRAILING_DISTANCE_PERCENT = env_decimal(
    "TRAILING_DISTANCE_PERCENT",
    "0.25",
)


# ============================================================
# TOTAL EXPOSURE / SAFETY CONTROLS
# ============================================================

MAX_FUND_EXPOSURE_PERCENT = env_decimal(
    "MAX_FUND_EXPOSURE_PERCENT",
    "40",
)

MAX_TOTAL_LEVERAGED_EXPOSURE_PERCENT = env_decimal(
    "MAX_TOTAL_LEVERAGED_EXPOSURE_PERCENT",
    "200",
)

MAX_LOSS_PER_TRADE_PERCENT = env_decimal(
    "MAX_LOSS_PER_TRADE_PERCENT",
    "10",
)

MAX_CONSECUTIVE_LOSSES = env_int(
    "MAX_CONSECUTIVE_LOSSES",
    3,
)

LOSS_COOLDOWN_MINUTES = env_int(
    "LOSS_COOLDOWN_MINUTES",
    30,
)

SIGNAL_EXPIRY_MINUTES = env_int(
    "SIGNAL_EXPIRY_MINUTES",
    3,
)


# ============================================================
# PROTECTION FLAGS
# ============================================================

ONE_DIRECTION_ONLY = env_bool(
    "ONE_DIRECTION_ONLY",
    True,
)

ANTI_DUPLICATE_ORDERS = env_bool(
    "ANTI_DUPLICATE_ORDERS",
    True,
)

TREND_REVERSAL_EXIT_ENABLED = env_bool(
    "TREND_REVERSAL_EXIT_ENABLED",
    True,
)


# ============================================================
# SIGNAL QUALITY CONFIGURATION
# ============================================================

REQUIRE_PRICE_CONFIRMATION = env_bool(
    "REQUIRE_PRICE_CONFIRMATION",
    True,
)

REQUIRE_EMA19_MOMENTUM = env_bool(
    "REQUIRE_EMA19_MOMENTUM",
    True,
)

MIN_EMA_SEPARATION_PERCENT = env_decimal(
    "MIN_EMA_SEPARATION_PERCENT",
    "0.005",
)


# ============================================================
# CRITICAL EXECUTION SAFETY SWITCH
#
# DO NOT CHANGE THIS TO TRUE YET.
# MODULE 0F-4A DOES NOT PLACE REAL ORDERS.
# ============================================================

LIVE_ORDER_EXECUTION = False


# ============================================================
# RUNTIME STATE
# ============================================================

MAX_CANDLES_STORED = 500

closed_prices = deque(
    maxlen=MAX_CANDLES_STORED
)

current_candle_start: Optional[int] = None
current_candle_close: Optional[Decimal] = None

previous_ema19: Optional[Decimal] = None
previous_ema50: Optional[Decimal] = None
previous_ema200: Optional[Decimal] = None

pending_signal: Optional[dict] = None

last_confirmed_signal: Optional[str] = None

closed_candle_counter = 0


# ============================================================
# RENDER LOGGING
# ============================================================

def render_log(
    message: str = "",
) -> None:

    print(
        message,
        flush=True,
    )


# ============================================================
# TELEGRAM HELPERS
# ============================================================

def telegram_is_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(
    message: str,
) -> None:

    if not telegram_is_configured():

        render_log(
            "TELEGRAM MESSAGE SKIPPED: CONFIG MISSING"
        )

        return

    try:

        bot = Bot(
            token=TELEGRAM_BOT_TOKEN
        )

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        render_log(
            "TELEGRAM MESSAGE SENT"
        )

    except Exception as error:

        render_log(
            "TELEGRAM ERROR: "
            f"{type(error).__name__}: "
            f"{error}"
        )


# ============================================================
# SAFE DECIMAL CONVERSION
# ============================================================

def to_decimal(
    value: Any,
) -> Optional[Decimal]:

    if value is None:
        return None

    try:

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


# ============================================================
# EMA CALCULATION
# ============================================================

def calculate_ema(
    prices,
    period: int,
) -> Optional[Decimal]:

    if len(prices) < period:
        return None

    multiplier = (
        Decimal("2")
        /
        Decimal(period + 1)
    )

    price_list = list(prices)

    starting_prices = (
        price_list[:period]
    )

    ema = (
        sum(starting_prices)
        /
        Decimal(period)
    )

    for price in price_list[period:]:

        ema = (
            (
                price - ema
            )
            * multiplier
            + ema
        )

    return ema


# ============================================================
# EMA STRUCTURE
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
            "🟡 EARLY BEARISH / "
            "WEAKENING STRUCTURE"
        )

    return (
        "⚪ MIXED / NEUTRAL EMA STRUCTURE"
    )


# ============================================================
# EMA SEPARATION
# ============================================================

def ema_separation_percent(
    ema_fast: Decimal,
    ema_slow: Decimal,
) -> Decimal:

    if ema_slow == 0:
        return Decimal("0")

    return (
        abs(
            ema_fast - ema_slow
        )
        /
        ema_slow
        * Decimal("100")
    )


# ============================================================
# SAFETY CONFIGURATION VALIDATION
# ============================================================

def validate_configuration() -> None:

    errors = []

    if (
        INITIAL_POSITION_PERCENT
        <= 0
    ):
        errors.append(
            "INITIAL_POSITION_PERCENT "
            "must be greater than 0"
        )

    if (
        LEVERAGE <= 0
    ):
        errors.append(
            "LEVERAGE must be greater than 0"
        )

    if (
        LEVERAGE
        > MAX_LEVERAGE
    ):
        errors.append(
            "LEVERAGE exceeds MAX_LEVERAGE"
        )

    if (
        MAX_PYRAMID_ADDS < 0
    ):
        errors.append(
            "MAX_PYRAMID_ADDS cannot be negative"
        )

    if (
        MAX_BACKUPS < 0
    ):
        errors.append(
            "MAX_BACKUPS cannot be negative"
        )

    if (
        MAX_BACKUPS > 3
    ):
        errors.append(
            "MAX_BACKUPS cannot exceed 3 "
            "in Module 0F-4A"
        )

    tp_total = (
        TP1_POSITION_PERCENT
        + TP2_POSITION_PERCENT
        + TP3_POSITION_PERCENT
    )

    if (
        tp_total
        != Decimal("100")
    ):
        errors.append(
            "TP1 + TP2 + TP3 position percentages "
            "must equal 100%"
        )

    if (
        MAX_FUND_EXPOSURE_PERCENT
        <= 0
        or
        MAX_FUND_EXPOSURE_PERCENT
        > 100
    ):
        errors.append(
            "MAX_FUND_EXPOSURE_PERCENT "
            "must be between 0 and 100"
        )

    if errors:

        render_log(
            "=" * 60
        )

        render_log(
            "CONFIGURATION VALIDATION FAILED"
        )

        for error in errors:

            render_log(
                f"ERROR: {error}"
            )

        render_log(
            "=" * 60
        )

        raise ValueError(
            "INVALID 0F-4A CONFIGURATION"
        )

    render_log(
        "CONFIGURATION VALIDATION: PASSED"
    )


# ============================================================
# STARTUP CONFIGURATION LOG
# ============================================================

def log_configuration() -> None:

    render_log(
        "=" * 60
    )

    render_log(
        f"MODULE {MODULE_NAME} STARTING"
    )

    render_log(
        f"{SYMBOL} SAFETY + "
        "TRADE CONFIGURATION ENGINE"
    )

    render_log(
        "EMA19 / EMA50 / EMA200"
    )

    render_log(
        "=" * 60
    )

    render_log(
        "TRADE CONFIGURATION"
    )

    render_log(
        f"INITIAL ENTRY: "
        f"{INITIAL_POSITION_PERCENT}%"
    )

    render_log(
        f"LEVERAGE: {LEVERAGE}x"
    )

    render_log(
        f"MAX LEVERAGE: {MAX_LEVERAGE}x"
    )

    render_log(
        "-" * 60
    )

    render_log(
        "PYRAMID CONFIGURATION"
    )

    render_log(
        f"MAX PYRAMIDS: "
        f"{MAX_PYRAMID_ADDS}"
    )

    render_log(
        f"PYRAMID 1 SIZE: "
        f"{PYRAMID_1_PERCENT}%"
    )

    render_log(
        f"PYRAMID 2 SIZE: "
        f"{PYRAMID_2_PERCENT}%"
    )

    render_log(
        f"PYRAMID 3 SIZE: "
        f"{PYRAMID_3_PERCENT}%"
    )

    render_log(
        "-" * 60
    )

    render_log(
        "BACKUP CONFIGURATION"
    )

    render_log(
        f"MAX BACKUPS: {MAX_BACKUPS}"
    )

    render_log(
        f"BACKUP 1 SIZE: "
        f"{BACKUP_1_PERCENT}%"
    )

    render_log(
        f"BACKUP 2 SIZE: "
        f"{BACKUP_2_PERCENT}%"
    )

    render_log(
        f"BACKUP 3 SIZE: "
        f"{BACKUP_3_PERCENT}%"
    )

    render_log(
        "BACKUP LIQUIDATION LEVEL: "
        "RECALCULATE AFTER EACH EXECUTION"
    )

    render_log(
        f"LIQUIDATION SAFETY BUFFER: "
        f"{LIQUIDATION_SAFETY_BUFFER_PERCENT}%"
    )

    render_log(
        f"MIN LIQUIDATION DISTANCE: "
        f"{MIN_LIQUIDATION_DISTANCE_PERCENT}%"
    )

    render_log(
        "-" * 60
    )

    render_log(
        "TAKE PROFIT CONFIGURATION"
    )

    render_log(
        f"TP1 POSITION: "
        f"{TP1_POSITION_PERCENT}%"
    )

    render_log(
        f"TP2 POSITION: "
        f"{TP2_POSITION_PERCENT}%"
    )

    render_log(
        f"TP3 TRAILING POSITION: "
        f"{TP3_POSITION_PERCENT}%"
    )

    render_log(
        f"TP1 TARGET: "
        f"{TP1_TARGET_PERCENT}%"
    )

    render_log(
        f"TP2 TARGET: "
        f"{TP2_TARGET_PERCENT}%"
    )

    render_log(
        f"TRAIL ACTIVATION: "
        f"{TRAILING_ACTIVATION_PERCENT}%"
    )

    render_log(
        f"TRAIL DISTANCE: "
        f"{TRAILING_DISTANCE_PERCENT}%"
    )

    render_log(
        "-" * 60
    )

    render_log(
        "SAFETY CONTROLS"
    )

    render_log(
        f"MAX FUND EXPOSURE: "
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    render_log(
        "MAX LEVERAGED EXPOSURE: "
        f"{MAX_TOTAL_LEVERAGED_EXPOSURE_PERCENT}%"
    )

    render_log(
        f"MAX LOSS PER TRADE: "
        f"{MAX_LOSS_PER_TRADE_PERCENT}%"
    )

    render_log(
        f"SIGNAL EXPIRY: "
        f"{SIGNAL_EXPIRY_MINUTES} MIN"
    )

    render_log(
        f"MAX CONSECUTIVE LOSSES: "
        f"{MAX_CONSECUTIVE_LOSSES}"
    )

    render_log(
        f"LOSS COOLDOWN: "
        f"{LOSS_COOLDOWN_MINUTES} MIN"
    )

    render_log(
        "ONE DIRECTION ONLY: "
        f"{ONE_DIRECTION_ONLY}"
    )

    render_log(
        "ANTI DUPLICATE ORDERS: "
        f"{ANTI_DUPLICATE_ORDERS}"
    )

    render_log(
        "TREND REVERSAL EXIT: "
        f"{TREND_REVERSAL_EXIT_ENABLED}"
    )

    render_log(
        "-" * 60
    )

    render_log(
        "SIGNAL QUALITY SETTINGS"
    )

    render_log(
        "PRICE CONFIRMATION: "
        f"{REQUIRE_PRICE_CONFIRMATION}"
    )

    render_log(
        "EMA19 MOMENTUM REQUIRED: "
        f"{REQUIRE_EMA19_MOMENTUM}"
    )

    render_log(
        "MIN EMA19/50 SEPARATION: "
        f"{MIN_EMA_SEPARATION_PERCENT}%"
    )

    render_log(
        "-" * 60
    )

    render_log(
        "SAFETY CONTROLS: ACTIVE"
    )

    render_log(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    render_log(
        "=" * 60
    )


# ============================================================
# HISTORICAL CANDLES
# ============================================================

async def load_historical_candles() -> None:

    render_log(
        "LOADING 1m HISTORICAL CANDLES..."
    )

    params = {
        "symbol": SYMBOL,
        "interval": HISTORICAL_INTERVAL,
        "limit": HISTORICAL_LIMIT,
    }

    headers = {
        "User-Agent":
            "WEEX-BTC-Bot/1.0",
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(
            HISTORICAL_URL,
            params=params,
            headers=headers,
        ) as response:

            render_log(
                "HISTORICAL HTTP STATUS: "
                f"{response.status}"
            )

            if response.status != 200:

                body = await response.text()

                render_log(
                    "HISTORICAL ERROR BODY: "
                    f"{body[:500]}"
                )

                raise RuntimeError(
                    "FAILED TO LOAD "
                    "HISTORICAL CANDLES"
                )

            data = await response.json()

    if not isinstance(
        data,
        list,
    ):

        raise RuntimeError(
            "UNEXPECTED HISTORICAL "
            "CANDLE RESPONSE"
        )

    parsed_candles = []

    for candle in data:

        if (
            not isinstance(candle, list)
            or len(candle) < 5
        ):
            continue

        try:

            open_time = int(
                candle[0]
            )

        except (
            ValueError,
            TypeError,
        ):

            continue

        close_price = to_decimal(
            candle[4]
        )

        if close_price is None:
            continue

        parsed_candles.append(
            (
                open_time,
                close_price,
            )
        )

    parsed_candles.sort(
        key=lambda item: item[0]
    )

    closed_prices.clear()

    for _, close_price in parsed_candles:

        closed_prices.append(
            close_price
        )

    render_log(
        "HISTORICAL CANDLES LOADED: "
        f"{len(closed_prices)}"
    )

    if (
        len(closed_prices)
        < 200
    ):

        raise RuntimeError(
            "NOT ENOUGH HISTORICAL "
            "CANDLES FOR EMA200"
        )

    render_log(
        "LATEST CLOSED PRICE: "
        f"{closed_prices[-1]}"
    )


# ============================================================
# INITIAL EMA ENGINE
# ============================================================

def initialize_ema_engine() -> None:

    global previous_ema19
    global previous_ema50
    global previous_ema200

    ema19 = calculate_ema(
        closed_prices,
        19,
    )

    ema50 = calculate_ema(
        closed_prices,
        50,
    )

    ema200 = calculate_ema(
        closed_prices,
        200,
    )

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):

        raise RuntimeError(
            "EMA INITIALIZATION FAILED"
        )

    previous_ema19 = ema19
    previous_ema50 = ema50
    previous_ema200 = ema200

    render_log(
        "INITIAL EMA ENGINE"
    )

    render_log(
        f"EMA19: {ema19:.2f}"
    )

    render_log(
        f"EMA50: {ema50:.2f}"
    )

    render_log(
        f"EMA200: {ema200:.2f}"
    )

    render_log(
        "STRUCTURE: "
        + describe_structure(
            ema19,
            ema50,
            ema200,
        )
    )

    render_log(
        "EMA ENGINE READY"
    )


# ============================================================
# SIGNAL QUALITY CHECK
# ============================================================

def signal_quality_passes(
    direction: str,
    close_price: Decimal,
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
    previous_fast: Decimal,
) -> tuple[bool, str]:

    separation = (
        ema_separation_percent(
            ema19,
            ema50,
        )
    )

    if (
        separation
        < MIN_EMA_SEPARATION_PERCENT
    ):

        return (
            False,
            "EMA19/50 separation too small",
        )

    if direction == "LONG":

        if not (
            ema19
            > ema50
            > ema200
        ):

            return (
                False,
                "Bullish EMA structure not confirmed",
            )

        if (
            REQUIRE_PRICE_CONFIRMATION
            and close_price <= ema19
        ):

            return (
                False,
                "Price is not above EMA19",
            )

        if (
            REQUIRE_EMA19_MOMENTUM
            and ema19 <= previous_fast
        ):

            return (
                False,
                "EMA19 bullish momentum not confirmed",
            )

        return (
            True,
            "Bullish quality filters passed",
        )

    if direction == "SHORT":

        if not (
            ema19
            < ema50
            < ema200
        ):

            return (
                False,
                "Bearish EMA structure not confirmed",
            )

        if (
            REQUIRE_PRICE_CONFIRMATION
            and close_price >= ema19
        ):

            return (
                False,
                "Price is not below EMA19",
            )

        if (
            REQUIRE_EMA19_MOMENTUM
            and ema19 >= previous_fast
        ):

            return (
                False,
                "EMA19 bearish momentum not confirmed",
            )

        return (
            True,
            "Bearish quality filters passed",
        )

    return (
        False,
        "Unknown direction",
    )


# ============================================================
# CONFIRMED SIGNAL
# ============================================================

async def confirm_signal(
    direction: str,
    close_price: Decimal,
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> None:

    global last_confirmed_signal

    if (
        ANTI_DUPLICATE_ORDERS
        and
        last_confirmed_signal
        == direction
    ):

        render_log(
            "SIGNAL BLOCKED: "
            f"DUPLICATE {direction}"
        )

        return

    last_confirmed_signal = direction

    icon = (
        "🟢"
        if direction == "LONG"
        else "🔴"
    )

    render_log(
        "=" * 60
    )

    render_log(
        f"{direction} SIGNAL CONFIRMED"
    )

    render_log(
        f"PRICE: {close_price}"
    )

    render_log(
        f"EMA19: {ema19:.2f}"
    )

    render_log(
        f"EMA50: {ema50:.2f}"
    )

    render_log(
        f"EMA200: {ema200:.2f}"
    )

    render_log(
        "QUALITY FILTER: PASSED"
    )

    render_log(
        "SAFETY ENGINE: ACTIVE"
    )

    render_log(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    render_log(
        "=" * 60
    )

    telegram_message = (
        f"{icon} {SYMBOL} "
        f"{direction} SIGNAL\n\n"
        f"✅ EMA19 / EMA50 CROSSOVER\n"
        f"✅ NEXT 1m CANDLE CONFIRMED\n"
        f"✅ SIGNAL QUALITY PASSED\n\n"
        f"Price: {close_price}\n"
        f"EMA19: {ema19:.2f}\n"
        f"EMA50: {ema50:.2f}\n"
        f"EMA200: {ema200:.2f}\n\n"
        f"🛡 Safety configuration active\n"
        f"⚠️ Live order execution disabled\n\n"
        f"MODULE {MODULE_NAME}"
    )

    await send_telegram(
        telegram_message
    )


# ============================================================
# CLOSED CANDLE PROCESSING
# ============================================================

async def process_closed_candle(
    close_price: Decimal,
) -> None:

    global previous_ema19
    global previous_ema50
    global previous_ema200
    global pending_signal
    global closed_candle_counter

    closed_prices.append(
        close_price
    )

    closed_candle_counter += 1

    ema19 = calculate_ema(
        closed_prices,
        19,
    )

    ema50 = calculate_ema(
        closed_prices,
        50,
    )

    ema200 = calculate_ema(
        closed_prices,
        200,
    )

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):
        return

    render_log(
        "=" * 60
    )

    render_log(
        f"MODULE {MODULE_NAME} "
        "- CLOSED 1m CANDLE"
    )

    render_log(
        f"{SYMBOL} CLOSE: "
        f"{close_price}"
    )

    render_log(
        f"EMA19: {ema19:.2f}"
    )

    render_log(
        f"EMA50: {ema50:.2f}"
    )

    render_log(
        f"EMA200: {ema200:.2f}"
    )

    render_log(
        "STRUCTURE: "
        + describe_structure(
            ema19,
            ema50,
            ema200,
        )
    )

    separation = (
        ema_separation_percent(
            ema19,
            ema50,
        )
    )

    render_log(
        "EMA19/50 SEPARATION: "
        f"{separation:.6f}%"
    )

    if (
        previous_ema19 is None
        or previous_ema50 is None
        or previous_ema200 is None
    ):

        previous_ema19 = ema19
        previous_ema50 = ema50
        previous_ema200 = ema200

        return

    old_ema19 = previous_ema19
    old_ema50 = previous_ema50

    # --------------------------------------------------------
    # FIRST CHECK AN EXISTING PENDING SIGNAL
    # --------------------------------------------------------

    if pending_signal is not None:

        direction = pending_signal[
            "direction"
        ]

        created_at_counter = pending_signal[
            "candle_counter"
        ]

        candles_elapsed = (
            closed_candle_counter
            - created_at_counter
        )

        render_log(
            "PENDING SIGNAL CHECK: "
            f"{direction}"
        )

        if candles_elapsed >= 1:

            quality_passed, reason = (
                signal_quality_passes(
                    direction=direction,
                    close_price=close_price,
                    ema19=ema19,
                    ema50=ema50,
                    ema200=ema200,
                    previous_fast=old_ema19,
                )
            )

            render_log(
                "QUALITY RESULT: "
                f"{quality_passed}"
            )

            render_log(
                "QUALITY REASON: "
                f"{reason}"
            )

            if quality_passed:

                await confirm_signal(
                    direction=direction,
                    close_price=close_price,
                    ema19=ema19,
                    ema50=ema50,
                    ema200=ema200,
                )

            else:

                render_log(
                    "PENDING SIGNAL REJECTED"
                )

            pending_signal = None

    # --------------------------------------------------------
    # DETECT NEW CROSSOVER
    # --------------------------------------------------------

    bullish_cross = (
        old_ema19
        <= old_ema50
        and
        ema19
        > ema50
    )

    bearish_cross = (
        old_ema19
        >= old_ema50
        and
        ema19
        < ema50
    )

    if (
        pending_signal is None
        and bullish_cross
    ):

        pending_signal = {
            "direction": "LONG",
            "candle_counter":
                closed_candle_counter,
            "price": close_price,
        }

        render_log(
            "CROSSOVER DETECTED: "
            "EMA19 ABOVE EMA50"
        )

        render_log(
            "SIGNAL ENTERED PENDING STATE"
        )

        render_log(
            "WAITING FOR NEXT CLOSED "
            "1m CANDLE CONFIRMATION"
        )

    elif (
        pending_signal is None
        and bearish_cross
    ):

        pending_signal = {
            "direction": "SHORT",
            "candle_counter":
                closed_candle_counter,
            "price": close_price,
        }

        render_log(
            "CROSSOVER DETECTED: "
            "EMA19 BELOW EMA50"
        )

        render_log(
            "SIGNAL ENTERED PENDING STATE"
        )

        render_log(
            "WAITING FOR NEXT CLOSED "
            "1m CANDLE CONFIRMATION"
        )

    previous_ema19 = ema19
    previous_ema50 = ema50
    previous_ema200 = ema200


# ============================================================
# WEBSOCKET MESSAGE PROCESSING
# ============================================================

async def handle_ws_message(
    websocket,
    raw_message: str,
) -> None:

    global current_candle_start
    global current_candle_close

    try:

        message = json.loads(
            raw_message
        )

    except json.JSONDecodeError:

        render_log(
            "NON-JSON WEBSOCKET MESSAGE "
            "IGNORED"
        )

        return

    # --------------------------------------------------------
    # WEEX PING
    # --------------------------------------------------------

    if (
        isinstance(message, dict)
        and message.get("event")
        == "ping"
    ):

        await websocket.send(
            json.dumps(
                {
                    "method": "PONG",
                    "id": 1,
                }
            )
        )

        return

    # --------------------------------------------------------
    # SUBSCRIPTION ACKNOWLEDGEMENT
    # --------------------------------------------------------

    if (
        isinstance(message, dict)
        and message.get("id") == 1
        and message.get("result")
        is True
    ):

        render_log(
            "SUBSCRIPTION CONFIRMED"
        )

        return

    # --------------------------------------------------------
    # KLINE MESSAGE
    # --------------------------------------------------------

    if not isinstance(
        message,
        dict,
    ):
        return

    if message.get("e") != "kline":
        return

    candle_data = message.get(
        "d"
    )

    if (
        not isinstance(
            candle_data,
            list,
        )
        or not candle_data
    ):

        return

    candle = candle_data[0]

    if not isinstance(
        candle,
        dict,
    ):

        return

    try:

        candle_start = int(
            candle.get("t")
        )

    except (
        TypeError,
        ValueError,
    ):

        return

    close_price = to_decimal(
        candle.get("c")
    )

    if close_price is None:
        return

    # --------------------------------------------------------
    # FIRST LIVE CANDLE
    # --------------------------------------------------------

    if current_candle_start is None:

        current_candle_start = (
            candle_start
        )

        current_candle_close = (
            close_price
        )

        render_log(
            "LIVE 1m CANDLE STARTED: "
            f"{close_price}"
        )

        return

    # --------------------------------------------------------
    # SAME FORMING CANDLE
    # --------------------------------------------------------

    if (
        candle_start
        == current_candle_start
    ):

        current_candle_close = (
            close_price
        )

        return

    # --------------------------------------------------------
    # NEW CANDLE MEANS PREVIOUS ONE CLOSED
    # --------------------------------------------------------

    if (
        candle_start
        > current_candle_start
    ):

        previous_close = (
            current_candle_close
        )

        current_candle_start = (
            candle_start
        )

        current_candle_close = (
            close_price
        )

        if previous_close is not None:

            await process_closed_candle(
                previous_close
            )

        render_log(
            "NEW LIVE 1m CANDLE: "
            f"{close_price}"
        )


# ============================================================
# WEBSOCKET CONNECTION
# ============================================================

async def run_websocket() -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    while True:

        try:

            headers = {
                "User-Agent":
                    "WEEX-BTC-Bot/1.0",
            }

            async with websockets.connect(
                WS_URL,
                additional_headers=headers,
                ping_interval=None,
                close_timeout=10,
            ) as websocket:

                render_log(
                    "CONNECTED TO WEEX"
                )

                subscribe_payload = {
                    "method": "SUBSCRIBE",
                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],
                    "id": 1,
                }

                await websocket.send(
                    json.dumps(
                        subscribe_payload
                    )
                )

                render_log(
                    "SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}"
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                async for raw_message in websocket:

                    await handle_ws_message(
                        websocket,
                        raw_message,
                    )

        except asyncio.CancelledError:

            raise

        except Exception as error:

            render_log(
                "=" * 60
            )

            render_log(
                "WEBSOCKET ERROR: "
                f"{type(error).__name__}: "
                f"{error}"
            )

            render_log(
                "RECONNECTING IN "
                f"{reconnect_delay} SECONDS"
            )

            render_log(
                "=" * 60
            )

            await asyncio.sleep(
                reconnect_delay
            )

            reconnect_delay = min(
                reconnect_delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


# ============================================================
# STARTUP TELEGRAM MESSAGE
# ============================================================

async def send_startup_message() -> None:

    telegram_status = (
        "READY"
        if telegram_is_configured()
        else "MISSING"
    )

    render_log(
        "TELEGRAM CONFIG: "
        f"{telegram_status}"
    )

    message = (
        f"✅ MODULE {MODULE_NAME} ONLINE\n\n"
        f"{SYMBOL}\n"
        f"Safety + Trade Configuration Engine\n"
        f"EMA19 / EMA50 / EMA200\n\n"
        f"Initial Entry: "
        f"{INITIAL_POSITION_PERCENT}%\n"
        f"Leverage: {LEVERAGE}x\n"
        f"Max Leverage: {MAX_LEVERAGE}x\n"
        f"Max Pyramids: "
        f"{MAX_PYRAMID_ADDS}\n"
        f"Max Backups: {MAX_BACKUPS}\n"
        f"TP1/TP2/TP3: "
        f"{TP1_POSITION_PERCENT}% / "
        f"{TP2_POSITION_PERCENT}% / "
        f"{TP3_POSITION_PERCENT}%\n\n"
        f"🛡 Safety controls active\n"
        f"⚠️ Live order execution disabled"
    )

    await send_telegram(
        message
    )


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    render_log(
        ""
    )

    log_configuration()

    validate_configuration()

    render_log(
        "TELEGRAM CONFIG: "
        + (
            "READY"
            if telegram_is_configured()
            else "MISSING"
        )
    )

    await load_historical_candles()

    initialize_ema_engine()

    await send_startup_message()

    render_log(
        "=" * 60
    )

    render_log(
        "LIVE SIGNAL MODE ACTIVE"
    )

    render_log(
        "PENDING CONFIRMATION ENGINE ACTIVE"
    )

    render_log(
        "SIGNAL QUALITY ENGINE ACTIVE"
    )

    render_log(
        "SAFETY CONFIGURATION ENGINE ACTIVE"
    )

    render_log(
        "LIVE ORDER EXECUTION DISABLED"
    )

    render_log(
        "=" * 60
    )

    await run_websocket()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        render_log(
            "MODULE STOPPED BY USER"
        )

    except Exception as error:

        render_log(
            "=" * 60
        )

        render_log(
            "FATAL ERROR: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        render_log(
            "=" * 60
        )

        raise
