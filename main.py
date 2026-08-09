import asyncio
import json
import os
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4A"

print("=" * 60)
print(f"MODULE {MODULE_NAME} STARTING")
print("BTCUSDT SAFETY + TRADE CONFIGURATION ENGINE")
print("EMA19 / EMA50 / EMA200")
print("CROSSOVER + PENDING CONFIRMATION + QUALITY FILTER")
print("RISK / PYRAMID / BACKUP / TP CONFIGURATION")
print("LIVE ORDER EXECUTION: DISABLED")
print("=" * 60)


# ============================================================
# GENERAL CONFIG HELPERS
# ============================================================

def env_decimal(name: str, default: str) -> Decimal:
    raw = os.getenv(name, default).strip()

    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        print(
            f"WARNING: INVALID {name}={raw!r}. "
            f"USING DEFAULT {default}"
        )
        return Decimal(default)


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()

    try:
        return int(raw)
    except ValueError:
        print(
            f"WARNING: INVALID {name}={raw!r}. "
            f"USING DEFAULT {default}"
        )
        return default


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(
        name,
        "true" if default else "false",
    ).strip().lower()

    return raw in {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }


# ============================================================
# MARKET CONFIGURATION
# ============================================================

# Deliberately kept as an environment variable so that
# multi-coin support can be added later without redesigning
# the complete strategy engine.

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

WS_URL = os.getenv(
    "WEEX_WS_URL",
    "wss://ws-contract.weex.com/v3/ws/public",
).strip()

HISTORICAL_URL = os.getenv(
    "WEEX_HISTORICAL_URL",
    "https://api-contract.weex.com/capi/v3/market/klines",
).strip()

SUBSCRIPTION_CHANNEL = (
    f"{SYMBOL}@kline_1m_LAST_PRICE"
)

HISTORICAL_LIMIT = 250

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
    bot: Optional[Bot],
    message: str,
) -> None:

    if bot is None:
        return

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print("TELEGRAM MESSAGE SENT")

    except Exception as exc:
        print(
            "TELEGRAM SEND ERROR:",
            repr(exc),
        )


# ============================================================
# 0F-3 SIGNAL QUALITY CONFIGURATION
# ============================================================

MIN_EMA19_50_SEPARATION_PERCENT = env_decimal(
    "MIN_EMA19_50_SEPARATION_PERCENT",
    "0.005",
)

PRICE_CONFIRMATION_ENABLED = env_bool(
    "PRICE_CONFIRMATION_ENABLED",
    True,
)

EMA19_MOMENTUM_ENABLED = env_bool(
    "EMA19_MOMENTUM_ENABLED",
    True,
)


# ============================================================
# 0F-4A INITIAL ENTRY CONFIGURATION
# ============================================================

# Percentage of the permitted account/trading allocation
# intended for the INITIAL entry.
#
# This is only CONFIGURED in 0F-4A.
# No actual WEEX order is submitted.

INITIAL_ENTRY_SIZE_PERCENT = env_decimal(
    "INITIAL_ENTRY_SIZE_PERCENT",
    "5",
)


# ============================================================
# 0F-4A LEVERAGE CONFIGURATION
# ============================================================

# Intended leverage for future execution module.

LEVERAGE = env_decimal(
    "LEVERAGE",
    "5",
)

# Absolute safety ceiling.

MAX_LEVERAGE = env_decimal(
    "MAX_LEVERAGE",
    "10",
)


# ============================================================
# 0F-4A PYRAMID CONFIGURATION
# ============================================================

MAX_PYRAMID_ADDS = env_int(
    "MAX_PYRAMID_ADDS",
    1,
)

# We support up to 10 future pyramid levels without
# requiring code editing.
#
# Only levels <= MAX_PYRAMID_ADDS are active.

MAX_SUPPORTED_PYRAMID_LEVELS = 10

PYRAMID_SIZE_PERCENTS = []

for level in range(
    1,
    MAX_SUPPORTED_PYRAMID_LEVELS + 1,
):
    value = env_decimal(
        f"PYRAMID_SIZE_{level}_PERCENT",
        "5",
    )

    PYRAMID_SIZE_PERCENTS.append(value)


# ============================================================
# PYRAMID MOMENTUM REQUIREMENTS
# ============================================================

# Additional positions must NEVER be added simply because
# price moved in the desired direction.
#
# Future execution modules will require renewed momentum
# confirmation before each pyramid.

PYRAMID_REQUIRE_EMA_ALIGNMENT = env_bool(
    "PYRAMID_REQUIRE_EMA_ALIGNMENT",
    True,
)

PYRAMID_REQUIRE_EMA19_MOMENTUM = env_bool(
    "PYRAMID_REQUIRE_EMA19_MOMENTUM",
    True,
)

PYRAMID_MIN_SEPARATION_PERCENT = env_decimal(
    "PYRAMID_MIN_SEPARATION_PERCENT",
    "0.01",
)


# ============================================================
# 0F-4A BACKUP CONFIGURATION
# ============================================================

MAX_BACKUPS = env_int(
    "MAX_BACKUPS",
    3,
)

MAX_SUPPORTED_BACKUP_LEVELS = 10

BACKUP_SIZE_PERCENTS = []

for level in range(
    1,
    MAX_SUPPORTED_BACKUP_LEVELS + 1,
):
    value = env_decimal(
        f"BACKUP_SIZE_{level}_PERCENT",
        "5",
    )

    BACKUP_SIZE_PERCENTS.append(value)


# Backup should be positioned relative to the CURRENT
# liquidation price.
#
# After each backup executes, future execution module MUST
# obtain/recalculate the NEW liquidation price before
# calculating the next backup.

BACKUP_LIQUIDATION_BUFFER_PERCENT = env_decimal(
    "BACKUP_LIQUIDATION_BUFFER_PERCENT",
    "0.30",
)

MIN_LIQUIDATION_DISTANCE_PERCENT = env_decimal(
    "MIN_LIQUIDATION_DISTANCE_PERCENT",
    "1.00",
)


# ============================================================
# TAKE-PROFIT CONFIGURATION
# ============================================================

# Percentage OF POSITION closed/managed by each TP stage.

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


# Profit target measured from average position entry.
# Adjustable from Render.

TP1_TARGET_PERCENT = env_decimal(
    "TP1_TARGET_PERCENT",
    "0.50",
)

TP2_TARGET_PERCENT = env_decimal(
    "TP2_TARGET_PERCENT",
    "1.00",
)


# TP3 trailing starts immediately after TP2 by default.
#
# Setting this to 0 means no additional profit move is
# required after TP2 before trailing becomes active.

TRAILING_ACTIVATION_PERCENT = env_decimal(
    "TRAILING_ACTIVATION_PERCENT",
    "0",
)

TRAILING_DISTANCE_PERCENT = env_decimal(
    "TRAILING_DISTANCE_PERCENT",
    "0.20",
)


# ============================================================
# ACCOUNT / EXPOSURE SAFETY
# ============================================================

# Maximum total combined exposure for:
#
# INITIAL ENTRY
# + PYRAMIDS
# + BACKUPS
#
# Future executor must block additional orders when this
# ceiling would be exceeded.

MAX_TOTAL_EXPOSURE_PERCENT = env_decimal(
    "MAX_TOTAL_EXPOSURE_PERCENT",
    "30",
)


# Maximum actual account funds permitted for one complete
# trade campaign.

MAX_FUND_EXPOSURE_PERCENT = env_decimal(
    "MAX_FUND_EXPOSURE_PERCENT",
    "20",
)


# Maximum permitted loss for the complete trade campaign.

MAX_TRADE_LOSS_PERCENT = env_decimal(
    "MAX_TRADE_LOSS_PERCENT",
    "5",
)


# ============================================================
# SIGNAL EXPIRY
# ============================================================

SIGNAL_EXPIRY_SECONDS = env_int(
    "SIGNAL_EXPIRY_SECONDS",
    180,
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

TREND_REVERSAL_EXIT = env_bool(
    "TREND_REVERSAL_EXIT",
    True,
)


# ============================================================
# LOSS COOLDOWN
# ============================================================

LOSS_COOLDOWN_SECONDS = env_int(
    "LOSS_COOLDOWN_SECONDS",
    300,
)


# ============================================================
# FUTURE MULTI-COIN PORTFOLIO SAFETY
# ============================================================

# Not actively used while running single-symbol BTCUSDT.
#
# Added now so 0F-4A architecture does not need to be
# redesigned when ETHUSDT / SOLUSDT etc. are introduced.

MAX_PORTFOLIO_EXPOSURE_PERCENT = env_decimal(
    "MAX_PORTFOLIO_EXPOSURE_PERCENT",
    "40",
)


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_percent(
    name: str,
    value: Decimal,
    minimum: Decimal = Decimal("0"),
    maximum: Decimal = Decimal("100"),
) -> None:

    if value < minimum or value > maximum:
        raise ValueError(
            f"{name} MUST BE BETWEEN "
            f"{minimum}% AND {maximum}%"
        )


def validate_configuration() -> None:

    print("=" * 60)
    print("VALIDATING 0F-4A CONFIGURATION")

    validate_percent(
        "INITIAL_ENTRY_SIZE_PERCENT",
        INITIAL_ENTRY_SIZE_PERCENT,
    )

    validate_percent(
        "MAX_TOTAL_EXPOSURE_PERCENT",
        MAX_TOTAL_EXPOSURE_PERCENT,
    )

    validate_percent(
        "MAX_FUND_EXPOSURE_PERCENT",
        MAX_FUND_EXPOSURE_PERCENT,
    )

    validate_percent(
        "MAX_TRADE_LOSS_PERCENT",
        MAX_TRADE_LOSS_PERCENT,
    )

    validate_percent(
        "MAX_PORTFOLIO_EXPOSURE_PERCENT",
        MAX_PORTFOLIO_EXPOSURE_PERCENT,
    )

    validate_percent(
        "TP1_POSITION_PERCENT",
        TP1_POSITION_PERCENT,
    )

    validate_percent(
        "TP2_POSITION_PERCENT",
        TP2_POSITION_PERCENT,
    )

    validate_percent(
        "TP3_POSITION_PERCENT",
        TP3_POSITION_PERCENT,
    )

    validate_percent(
        "TP1_TARGET_PERCENT",
        TP1_TARGET_PERCENT,
    )

    validate_percent(
        "TP2_TARGET_PERCENT",
        TP2_TARGET_PERCENT,
    )

    validate_percent(
        "TRAILING_ACTIVATION_PERCENT",
        TRAILING_ACTIVATION_PERCENT,
    )

    validate_percent(
        "TRAILING_DISTANCE_PERCENT",
        TRAILING_DISTANCE_PERCENT,
    )

    validate_percent(
        "BACKUP_LIQUIDATION_BUFFER_PERCENT",
        BACKUP_LIQUIDATION_BUFFER_PERCENT,
    )

    validate_percent(
        "MIN_LIQUIDATION_DISTANCE_PERCENT",
        MIN_LIQUIDATION_DISTANCE_PERCENT,
    )

    if LEVERAGE <= 0:
        raise ValueError(
            "LEVERAGE MUST BE GREATER THAN ZERO"
        )

    if MAX_LEVERAGE <= 0:
        raise ValueError(
            "MAX_LEVERAGE MUST BE GREATER THAN ZERO"
        )

    if LEVERAGE > MAX_LEVERAGE:
        raise ValueError(
            "LEVERAGE CANNOT EXCEED MAX_LEVERAGE"
        )

    if MAX_PYRAMID_ADDS < 0:
        raise ValueError(
            "MAX_PYRAMID_ADDS CANNOT BE NEGATIVE"
        )

    if (
        MAX_PYRAMID_ADDS
        > MAX_SUPPORTED_PYRAMID_LEVELS
    ):
        raise ValueError(
            "MAX_PYRAMID_ADDS EXCEEDS "
            f"SUPPORTED LIMIT "
            f"{MAX_SUPPORTED_PYRAMID_LEVELS}"
        )

    if MAX_BACKUPS < 0:
        raise ValueError(
            "MAX_BACKUPS CANNOT BE NEGATIVE"
        )

    if (
        MAX_BACKUPS
        > MAX_SUPPORTED_BACKUP_LEVELS
    ):
        raise ValueError(
            "MAX_BACKUPS EXCEEDS "
            f"SUPPORTED LIMIT "
            f"{MAX_SUPPORTED_BACKUP_LEVELS}"
        )

    if SIGNAL_EXPIRY_SECONDS <= 0:
        raise ValueError(
            "SIGNAL_EXPIRY_SECONDS MUST BE > 0"
        )

    if LOSS_COOLDOWN_SECONDS < 0:
        raise ValueError(
            "LOSS_COOLDOWN_SECONDS CANNOT BE NEGATIVE"
        )

    tp_total = (
        TP1_POSITION_PERCENT
        + TP2_POSITION_PERCENT
        + TP3_POSITION_PERCENT
    )

    if tp_total != Decimal("100"):
        raise ValueError(
            "TP POSITION PERCENTAGES MUST TOTAL 100%. "
            f"CURRENT TOTAL={tp_total}%"
        )

    active_pyramid_total = sum(
        PYRAMID_SIZE_PERCENTS[
            :MAX_PYRAMID_ADDS
        ],
        Decimal("0"),
    )

    active_backup_total = sum(
        BACKUP_SIZE_PERCENTS[
            :MAX_BACKUPS
        ],
        Decimal("0"),
    )

    theoretical_campaign_allocation = (
        INITIAL_ENTRY_SIZE_PERCENT
        + active_pyramid_total
        + active_backup_total
    )

    print(
        "THEORETICAL CONFIGURED CAMPAIGN SIZE:",
        f"{theoretical_campaign_allocation}%",
    )

    if (
        theoretical_campaign_allocation
        > MAX_TOTAL_EXPOSURE_PERCENT
    ):
        print(
            "WARNING: CONFIGURED ENTRY + PYRAMIDS "
            "+ BACKUPS CAN EXCEED "
            "MAX_TOTAL_EXPOSURE_PERCENT."
        )

        print(
            "THIS IS ALLOWED AS CONFIGURATION, "
            "BUT FUTURE EXECUTION ENGINE MUST "
            "BLOCK ADDITIONS AT THE SAFETY LIMIT."
        )

    print("CONFIGURATION VALIDATION: PASSED")
    print("=" * 60)


# ============================================================
# PRINT CONFIGURATION
# ============================================================

def print_configuration() -> None:

    print("=" * 60)
    print("0F-4A ACTIVE CONFIGURATION")
    print("=" * 60)

    print("SYMBOL:", SYMBOL)

    print("-" * 60)
    print("SIGNAL QUALITY")

    print(
        "MIN EMA19/50 SEPARATION:",
        f"{MIN_EMA19_50_SEPARATION_PERCENT}%",
    )

    print(
        "PRICE CONFIRMATION:",
        (
            "ENABLED"
            if PRICE_CONFIRMATION_ENABLED
            else "DISABLED"
        ),
    )

    print(
        "EMA19 MOMENTUM:",
        (
            "ENABLED"
            if EMA19_MOMENTUM_ENABLED
            else "DISABLED"
        ),
    )

    print("-" * 60)
    print("INITIAL ENTRY")

    print(
        "INITIAL ENTRY SIZE:",
        f"{INITIAL_ENTRY_SIZE_PERCENT}%",
    )

    print(
        "LEVERAGE:",
        f"{LEVERAGE}x",
    )

    print(
        "MAX LEVERAGE:",
        f"{MAX_LEVERAGE}x",
    )

    print("-" * 60)
    print("PYRAMID SETTINGS")

    print(
        "MAX PYRAMID ADDS:",
        MAX_PYRAMID_ADDS,
    )

    for i in range(MAX_PYRAMID_ADDS):
        print(
            f"PYRAMID {i + 1} SIZE:",
            f"{PYRAMID_SIZE_PERCENTS[i]}%",
        )

    print(
        "PYRAMID MIN SEPARATION:",
        f"{PYRAMID_MIN_SEPARATION_PERCENT}%",
    )

    print("-" * 60)
    print("BACKUP SETTINGS")

    print(
        "MAX BACKUPS:",
        MAX_BACKUPS,
    )

    for i in range(MAX_BACKUPS):
        print(
            f"BACKUP {i + 1} SIZE:",
            f"{BACKUP_SIZE_PERCENTS[i]}%",
        )

    print(
        "BACKUP LIQUIDATION BUFFER:",
        f"{BACKUP_LIQUIDATION_BUFFER_PERCENT}%",
    )

    print(
        "MIN LIQUIDATION DISTANCE:",
        f"{MIN_LIQUIDATION_DISTANCE_PERCENT}%",
    )

    print("-" * 60)
    print("TAKE PROFIT")

    print(
        "TP1 POSITION:",
        f"{TP1_POSITION_PERCENT}%",
    )

    print(
        "TP1 TARGET:",
        f"{TP1_TARGET_PERCENT}%",
    )

    print(
        "TP2 POSITION:",
        f"{TP2_POSITION_PERCENT}%",
    )

    print(
        "TP2 TARGET:",
        f"{TP2_TARGET_PERCENT}%",
    )

    print(
        "TP3 TRAILING POSITION:",
        f"{TP3_POSITION_PERCENT}%",
    )

    print(
        "TRAILING ACTIVATION:",
        f"{TRAILING_ACTIVATION_PERCENT}%",
    )

    print(
        "TRAILING DISTANCE:",
        f"{TRAILING_DISTANCE_PERCENT}%",
    )

    print("-" * 60)
    print("SAFETY LIMITS")

    print(
        "MAX TOTAL EXPOSURE:",
        f"{MAX_TOTAL_EXPOSURE_PERCENT}%",
    )

    print(
        "MAX FUND EXPOSURE:",
        f"{MAX_FUND_EXPOSURE_PERCENT}%",
    )

    print(
        "MAX TRADE LOSS:",
        f"{MAX_TRADE_LOSS_PERCENT}%",
    )

    print(
        "MAX PORTFOLIO EXPOSURE:",
        f"{MAX_PORTFOLIO_EXPOSURE_PERCENT}%",
    )

    print(
        "SIGNAL EXPIRY:",
        f"{SIGNAL_EXPIRY_SECONDS}s",
    )

    print(
        "LOSS COOLDOWN:",
        f"{LOSS_COOLDOWN_SECONDS}s",
    )

    print("-" * 60)
    print("PROTECTIONS")

    print(
        "ONE DIRECTION ONLY:",
        ONE_DIRECTION_ONLY,
    )

    print(
        "ANTI DUPLICATE ORDERS:",
        ANTI_DUPLICATE_ORDERS,
    )

    print(
        "TREND REVERSAL EXIT:",
        TREND_REVERSAL_EXIT,
    )

    print("-" * 60)
    print("ORDER EXECUTION: DISABLED")
    print("=" * 60)


# ============================================================
# EMA FUNCTIONS
# ============================================================

def calculate_ema(
    prices: list[Decimal],
    period: int,
) -> Decimal:

    if len(prices) < period:
        raise ValueError(
            f"NOT ENOUGH PRICES FOR EMA{period}"
        )

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    initial = (
        sum(
            prices[:period],
            Decimal("0"),
        )
        / Decimal(period)
    )

    ema = initial

    for price in prices[period:]:
        ema = (
            (price - ema)
            * multiplier
            + ema
        )

    return ema


def update_ema(
    previous_ema: Decimal,
    price: Decimal,
    period: int,
) -> Decimal:

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    return (
        (price - previous_ema)
        * multiplier
        + previous_ema
    )


# ============================================================
# EMA / SIGNAL STATE
# ============================================================

ema19: Optional[Decimal] = None
ema50: Optional[Decimal] = None
ema200: Optional[Decimal] = None

previous_ema19: Optional[Decimal] = None
previous_ema50: Optional[Decimal] = None
previous_ema200: Optional[Decimal] = None

last_processed_candle_id: Optional[str] = None


@dataclass
class PendingSignal:
    direction: str
    created_at: float
    crossover_candle_id: str
    crossover_price: Decimal


pending_signal: Optional[PendingSignal] = None

last_confirmed_direction: Optional[str] = None


# ============================================================
# MARKET STRUCTURE
# ============================================================

def market_structure(
    e19: Decimal,
    e50: Decimal,
    e200: Decimal,
) -> str:

    if e19 > e50 > e200:
        return (
            "🟢 STRONG BULLISH "
            "EMA19 > EMA50 > EMA200"
        )

    if e19 < e50 < e200:
        return (
            "🔴 STRONG BEARISH "
            "EMA19 < EMA50 < EMA200"
        )

    if e19 > e50:
        return (
            "🟡 EARLY BULLISH / "
            "RECOVERY STRUCTURE"
        )

    if e19 < e50:
        return (
            "🟡 EARLY BEARISH / "
            "WEAKENING STRUCTURE"
        )

    return "⚪ NEUTRAL STRUCTURE"


# ============================================================
# QUALITY FILTER
# ============================================================

def percentage_distance(
    value_a: Decimal,
    value_b: Decimal,
) -> Decimal:

    if value_b == 0:
        return Decimal("0")

    return (
        abs(value_a - value_b)
        / abs(value_b)
        * Decimal("100")
    )


def quality_filter_passes(
    direction: str,
    close_price: Decimal,
) -> tuple[bool, str]:

    global ema19
    global ema50
    global ema200
    global previous_ema19

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):
        return False, "EMA DATA NOT READY"

    separation = percentage_distance(
        ema19,
        ema50,
    )

    if (
        separation
        < MIN_EMA19_50_SEPARATION_PERCENT
    ):
        return (
            False,
            (
                "EMA19/50 SEPARATION TOO SMALL: "
                f"{separation:.5f}%"
            ),
        )

    if direction == "LONG":

        if not (
            ema19 > ema50 > ema200
        ):
            return (
                False,
                "LONG EMA ALIGNMENT FAILED",
            )

        if (
            PRICE_CONFIRMATION_ENABLED
            and close_price <= ema19
        ):
            return (
                False,
                "LONG PRICE CONFIRMATION FAILED",
            )

        if (
            EMA19_MOMENTUM_ENABLED
            and previous_ema19 is not None
            and ema19 <= previous_ema19
        ):
            return (
                False,
                "LONG EMA19 MOMENTUM FAILED",
            )

    elif direction == "SHORT":

        if not (
            ema19 < ema50 < ema200
        ):
            return (
                False,
                "SHORT EMA ALIGNMENT FAILED",
            )

        if (
            PRICE_CONFIRMATION_ENABLED
            and close_price >= ema19
        ):
            return (
                False,
                "SHORT PRICE CONFIRMATION FAILED",
            )

        if (
            EMA19_MOMENTUM_ENABLED
            and previous_ema19 is not None
            and ema19 >= previous_ema19
        ):
            return (
                False,
                "SHORT EMA19 MOMENTUM FAILED",
            )

    else:
        return (
            False,
            "UNKNOWN SIGNAL DIRECTION",
        )

    return (
        True,
        (
            "QUALITY FILTER PASSED "
            f"| EMA19/50 SEPARATION "
            f"{separation:.5f}%"
        ),
    )


# ============================================================
# SIGNAL EXPIRY
# ============================================================

def pending_signal_expired(
    signal: PendingSignal,
) -> bool:

    age = (
        time.time()
        - signal.created_at
    )

    return (
        age
        > SIGNAL_EXPIRY_SECONDS
    )


# ============================================================
# CROSSOVER DETECTION
# ============================================================

def detect_crossover() -> Optional[str]:

    if (
        previous_ema19 is None
        or previous_ema50 is None
        or ema19 is None
        or ema50 is None
    ):
        return None

    bullish = (
        previous_ema19 <= previous_ema50
        and ema19 > ema50
    )

    bearish = (
        previous_ema19 >= previous_ema50
        and ema19 < ema50
    )

    if bullish:
        return "LONG"

    if bearish:
        return "SHORT"

    return None


# ============================================================
# CONFIRMED SIGNAL HANDLER
# ============================================================

async def confirmed_signal(
    bot: Optional[Bot],
    direction: str,
    price: Decimal,
) -> None:

    global last_confirmed_direction

    # This is SIGNAL ONLY.
    #
    # 0F-4A MUST NOT submit an exchange order.

    if (
        ONE_DIRECTION_ONLY
        and last_confirmed_direction == direction
    ):
        print(
            "ANTI-DUPLICATE SIGNAL PROTECTION:",
            direction,
        )
        return

    last_confirmed_direction = direction

    emoji = (
        "🟢"
        if direction == "LONG"
        else "🔴"
    )

    message = (
        f"{emoji} {SYMBOL} {direction} SIGNAL\n\n"
        f"✅ EMA19 / EMA50 CROSSOVER\n"
        f"✅ NEXT 1m CANDLE CONFIRMED\n"
        f"✅ 0F-3 QUALITY FILTER PASSED\n\n"
        f"Price: {price}\n"
        f"EMA19: {ema19:.2f}\n"
        f"EMA50: {ema50:.2f}\n"
        f"EMA200: {ema200:.2f}\n\n"
        f"INITIAL ENTRY CONFIG: "
        f"{INITIAL_ENTRY_SIZE_PERCENT}%\n"
        f"LEVERAGE CONFIG: {LEVERAGE}x\n\n"
        f"⚠️ MODULE {MODULE_NAME}\n"
        f"ORDER EXECUTION DISABLED"
    )

    print("=" * 60)
    print(
        f"{direction} SIGNAL CONFIRMED"
    )
    print(
        "PRICE:",
        price,
    )
    print(
        "INITIAL ENTRY CONFIG:",
        f"{INITIAL_ENTRY_SIZE_PERCENT}%",
    )
    print(
        "NO LIVE ORDER SUBMITTED"
    )
    print("=" * 60)

    await send_telegram(
        bot,
        message,
    )


# ============================================================
# CLOSED CANDLE PROCESSING
# ============================================================

async def process_closed_candle(
    bot: Optional[Bot],
    close_price: Decimal,
    candle_id: str,
) -> None:

    global ema19
    global ema50
    global ema200

    global previous_ema19
    global previous_ema50
    global previous_ema200

    global pending_signal

    previous_ema19 = ema19
    previous_ema50 = ema50
    previous_ema200 = ema200

    if (
        ema19 is None
        or ema50 is None
        or ema200 is None
    ):
        return

    ema19 = update_ema(
        ema19,
        close_price,
        19,
    )

    ema50 = update_ema(
        ema50,
        close_price,
        50,
    )

    ema200 = update_ema(
        ema200,
        close_price,
        200,
    )

    print("=" * 60)
    print(
        f"MODULE {MODULE_NAME} - "
        "CLOSED 1m CANDLE"
    )

    print(
        f"{SYMBOL} CLOSE:",
        close_price,
    )

    print(
        "EMA19:",
        f"{ema19:.2f}",
    )

    print(
        "EMA50:",
        f"{ema50:.2f}",
    )

    print(
        "EMA200:",
        f"{ema200:.2f}",
    )

    print(
        "STRUCTURE:",
        market_structure(
            ema19,
            ema50,
            ema200,
        ),
    )

    # --------------------------------------------------------
    # FIRST: PROCESS EXISTING PENDING SIGNAL
    # --------------------------------------------------------

    if pending_signal is not None:

        if pending_signal_expired(
            pending_signal
        ):
            print(
                "PENDING SIGNAL EXPIRED:",
                pending_signal.direction,
            )

            pending_signal = None

        elif (
            candle_id
            != pending_signal.crossover_candle_id
        ):
            direction = (
                pending_signal.direction
            )

            quality_ok, reason = (
                quality_filter_passes(
                    direction,
                    close_price,
                )
            )

            print(
                "PENDING SIGNAL CHECK:",
                direction,
            )

            print(
                "QUALITY RESULT:",
                reason,
            )

            if quality_ok:
                await confirmed_signal(
                    bot,
                    direction,
                    close_price,
                )

            else:
                print(
                    "PENDING SIGNAL REJECTED"
                )

            # Pending signal is consumed after
            # the next closed candle.
            pending_signal = None

    # --------------------------------------------------------
    # SECOND: LOOK FOR NEW CROSSOVER
    # --------------------------------------------------------

    crossover = detect_crossover()

    if crossover is not None:

        pending_signal = PendingSignal(
            direction=crossover,
            created_at=time.time(),
            crossover_candle_id=candle_id,
            crossover_price=close_price,
        )

        print(
            f"{crossover} CROSSOVER DETECTED"
        )

        print(
            "SIGNAL ENTERED PENDING STATE"
        )

        print(
            "WAITING FOR NEXT CLOSED "
            "1m CANDLE"
        )


# ============================================================
# HISTORICAL DATA PARSING
# ============================================================

def decimal_or_none(
    value: Any,
) -> Optional[Decimal]:

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


def extract_close_from_row(
    row: Any,
) -> Optional[Decimal]:

    # Common kline list forms:
    #
    # [timestamp, open, high, low, close, ...]
    #
    # WEEX responses may vary, so several
    # formats are tolerated.

    if isinstance(row, list):

        if len(row) >= 5:
            close = decimal_or_none(
                row[4]
            )

            if close is not None:
                return close

        return None

    if isinstance(row, dict):

        for key in (
            "close",
            "c",
            "closePrice",
            "last",
            "lastPrice",
            "price",
        ):
            if key in row:
                close = decimal_or_none(
                    row[key]
                )

                if close is not None:
                    return close

    return None


def find_kline_rows(
    payload: Any,
) -> list[Any]:

    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    candidates = [
        payload.get("data"),
        payload.get("result"),
        payload.get("rows"),
        payload.get("list"),
    ]

    for candidate in candidates:

        if isinstance(candidate, list):
            return candidate

        if isinstance(candidate, dict):

            for key in (
                "list",
                "rows",
                "data",
            ):
                nested = candidate.get(key)

                if isinstance(
                    nested,
                    list,
                ):
                    return nested

    return []


# ============================================================
# LOAD HISTORICAL CANDLES
# ============================================================

async def load_historical_candles() -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES..."
    )

    parameter_sets = [
        {
            "symbol": SYMBOL,
            "interval": "1m",
            "limit": HISTORICAL_LIMIT,
        },
        {
            "symbol": SYMBOL,
            "period": "1m",
            "limit": HISTORICAL_LIMIT,
        },
    ]

    headers = {
        "User-Agent":
            "WEEX-BTC-Bot/1.0",
    }

    timeout = aiohttp.ClientTimeout(
        total=20,
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=headers,
    ) as session:

        for params in parameter_sets:

            try:
                async with session.get(
                    HISTORICAL_URL,
                    params=params,
                ) as response:

                    print(
                        "HISTORICAL HTTP STATUS:",
                        response.status,
                    )

                    if response.status != 200:
                        continue

                    payload = (
                        await response.json(
                            content_type=None
                        )
                    )

                    rows = find_kline_rows(
                        payload
                    )

                    prices = []

                    for row in rows:
                        close = (
                            extract_close_from_row(
                                row
                            )
                        )

                        if close is not None:
                            prices.append(close)

                    if len(prices) >= 200:

                        # Some APIs return newest-first.
                        # Attempt basic timestamp detection
                        # and reverse if necessary.

                        if (
                            len(rows) >= 2
                            and isinstance(
                                rows[0],
                                list,
                            )
                            and isinstance(
                                rows[1],
                                list,
                            )
                            and len(rows[0]) > 0
                            and len(rows[1]) > 0
                        ):
                            try:
                                first_ts = Decimal(
                                    str(rows[0][0])
                                )

                                second_ts = Decimal(
                                    str(rows[1][0])
                                )

                                if first_ts > second_ts:
                                    prices.reverse()

                            except Exception:
                                pass

                        print(
                            "HISTORICAL CANDLES LOADED:",
                            len(prices),
                        )

                        print(
                            "LATEST CLOSED PRICE:",
                            prices[-1],
                        )

                        return prices

            except Exception as exc:
                print(
                    "HISTORICAL LOAD ERROR:",
                    repr(exc),
                )

    return []


# ============================================================
# INITIALIZE EMA ENGINE
# ============================================================

async def initialize_ema_engine() -> None:

    global ema19
    global ema50
    global ema200

    prices = (
        await load_historical_candles()
    )

    if len(prices) < 200:
        raise RuntimeError(
            "NOT ENOUGH HISTORICAL "
            "CANDLES FOR EMA200"
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

    print("=" * 60)
    print("INITIAL EMA ENGINE")

    print(
        "EMA19:",
        f"{ema19:.2f}",
    )

    print(
        "EMA50:",
        f"{ema50:.2f}",
    )

    print(
        "EMA200:",
        f"{ema200:.2f}",
    )

    print(
        "STRUCTURE:",
        market_structure(
            ema19,
            ema50,
            ema200,
        ),
    )

    print("EMA ENGINE READY")
    print("=" * 60)


# ============================================================
# WEBSOCKET CANDLE PARSING
# ============================================================

def extract_candle_message(
    payload: Any,
) -> Optional[
    tuple[
        Decimal,
        str,
        bool,
    ]
]:

    if not isinstance(
        payload,
        dict,
    ):
        return None

    data = payload.get(
        "data"
    )

    # Sometimes data arrives inside list.

    if (
        isinstance(data, list)
        and data
    ):
        if isinstance(
            data[0],
            dict,
        ):
            data = data[0]

        elif isinstance(
            data[0],
            list,
        ):
            row = data[0]

            if len(row) >= 5:

                close = decimal_or_none(
                    row[4]
                )

                if close is None:
                    return None

                candle_id = str(
                    row[0]
                )

                # Kline streams often send only
                # completed rows. Treat this as
                # closed if no explicit flag exists.

                return (
                    close,
                    candle_id,
                    True,
                )

    if not isinstance(
        data,
        dict,
    ):
        return None

    close = None

    for key in (
        "close",
        "c",
        "closePrice",
        "price",
        "lastPrice",
    ):

        if key in data:
            close = decimal_or_none(
                data[key]
            )

            if close is not None:
                break

    if close is None:
        return None

    candle_id = None

    for key in (
        "startTime",
        "start",
        "timestamp",
        "ts",
        "time",
        "t",
    ):

        if key in data:
            candle_id = str(
                data[key]
            )
            break

    if candle_id is None:
        return None

    closed = False

    for key in (
        "closed",
        "isClosed",
        "confirm",
        "final",
        "x",
    ):

        if key in data:

            value = data[key]

            if isinstance(
                value,
                bool,
            ):
                closed = value

            elif str(
                value
            ).lower() in {
                "1",
                "true",
                "yes",
            }:
                closed = True

            break

    return (
        close,
        candle_id,
        closed,
    )


# ============================================================
# APPLICATION PING HANDLER
# ============================================================

async def handle_application_ping(
    websocket,
    payload: Any,
) -> bool:

    if not isinstance(
        payload,
        dict,
    ):
        return False

    if payload.get(
        "event"
    ) == "ping":

        await websocket.send(
            json.dumps(
                {
                    "event": "pong",
                }
            )
        )

        return True

    if "ping" in payload:

        await websocket.send(
            json.dumps(
                {
                    "pong":
                        payload["ping"],
                }
            )
        )

        return True

    return False


# ============================================================
# WEBSOCKET LIVE LOOP
# ============================================================

async def websocket_loop(
    bot: Optional[Bot],
) -> None:

    global last_processed_candle_id

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    while True:

        try:
            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                        "WEEX-BTC-Bot/1.0",
                },
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
                open_timeout=20,
            ) as websocket:

                print("CONNECTED TO WEEX")

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
                    "SUBSCRIBED TO",
                    SUBSCRIPTION_CHANNEL,
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                async for raw in websocket:

                    try:
                        payload = (
                            json.loads(raw)
                        )

                    except json.JSONDecodeError:
                        continue

                    if (
                        await handle_application_ping(
                            websocket,
                            payload,
                        )
                    ):
                        continue

                    if (
                        isinstance(
                            payload,
                            dict,
                        )
                        and (
                            payload.get(
                                "result"
                            )
                            is True
                        )
                    ):
                        print(
                            "SUBSCRIPTION CONFIRMED"
                        )
                        continue

                    candle = (
                        extract_candle_message(
                            payload
                        )
                    )

                    if candle is None:
                        continue

                    (
                        close_price,
                        candle_id,
                        closed,
                    ) = candle

                    if not closed:
                        continue

                    if (
                        candle_id
                        == last_processed_candle_id
                    ):
                        continue

                    last_processed_candle_id = (
                        candle_id
                    )

                    await process_closed_candle(
                        bot,
                        close_price,
                        candle_id,
                    )

        except asyncio.CancelledError:
            raise

        except Exception as exc:

            print(
                "WEBSOCKET ERROR:",
                repr(exc),
            )

            print(
                "RECONNECTING IN",
                reconnect_delay,
                "SECONDS",
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

async def send_startup_message(
    bot: Optional[Bot],
) -> None:

    if bot is None:
        return

    message = (
        f"✅ MODULE {MODULE_NAME} ONLINE\n\n"
        f"{SYMBOL}\n"
        f"Safety + Trade Configuration Engine\n"
        f"EMA19 / EMA50 / EMA200\n\n"
        f"Initial Entry: "
        f"{INITIAL_ENTRY_SIZE_PERCENT}%\n"
        f"Leverage: {LEVERAGE}x\n"
        f"Max Leverage: {MAX_LEVERAGE}x\n"
        f"Max Pyramids: {MAX_PYRAMID_ADDS}\n"
        f"Max Backups: {MAX_BACKUPS}\n"
        f"TP1/TP2/TP3: "
        f"{TP1_POSITION_PERCENT}% / "
        f"{TP2_POSITION_PERCENT}% / "
        f"{TP3_POSITION_PERCENT}%\n\n"
        f"🛡 Safety controls active\n"
        f"⚠️ Live order execution disabled"
    )

    await send_telegram(
        bot,
        message,
    )


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    validate_configuration()
    print_configuration()

    if telegram_is_configured():

        print(
            "TELEGRAM CONFIG: READY"
        )

        bot: Optional[Bot] = Bot(
            token=TELEGRAM_BOT_TOKEN
        )

    else:

        print(
            "TELEGRAM CONFIG: MISSING"
        )

        bot = None

    await initialize_ema_engine()

    print("=" * 60)
    print("LIVE SIGNAL MODE ACTIVE")
    print(
        "PENDING CONFIRMATION ENGINE ACTIVE"
    )
    print(
        "0F-3 QUALITY FILTER ACTIVE"
    )
    print(
        "0F-4A SAFETY CONFIGURATION ACTIVE"
    )
    print(
        "SIMULATED TEST DISABLED"
    )
    print(
        "LIVE ORDER EXECUTION DISABLED"
    )
    print("=" * 60)

    await send_startup_message(
        bot
    )

    await websocket_loop(
        bot
    )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        print(
            f"MODULE {MODULE_NAME} STOPPED"
        )

    except Exception as exc:
        print(
            "FATAL ERROR:",
            repr(exc),
        )
        raise
