#!/usr/bin/env python3

"""
FRESH WEEX TRADING BOT RECONSTRUCTION

UNIT 1
FOUNDATION / CONFIGURATION / SAFETY

PURPOSE
-------
Build a clean, independently testable foundation for the
parallel reconstruction of the BTCUSDT WEEX trading bot.

THIS UNIT DOES NOT:
- connect to WEEX
- read WEEX account data
- submit demo orders
- submit real orders
- change leverage
- change margin mode
- change positions
- read Telegram
- generate trading signals

The frozen 15,019-line bot is a behavioral reference only.
This implementation does not inherit its architecture.

UNIT 1 SUCCESS CONDITION
------------------------
All self-tests must PASS.

ZERO EXCHANGE WRITES.
ZERO DEMO ORDERS.
ZERO REAL ORDERS.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Any


# ============================================================
# APPLICATION IDENTITY
# ============================================================

APP_NAME = "WEEX_PARALLEL_BOT"

APP_VERSION = "0.1.0"

RECONSTRUCTION_UNIT = "UNIT_1_FOUNDATION"


# ============================================================
# DECIMAL HELPER
# ============================================================

def D(value: Any) -> Decimal:
    """
    Convert a value safely to Decimal through its string
    representation.

    Avoids binary floating-point contamination.
    """

    return Decimal(str(value))


# ============================================================
# TIME
# ============================================================

def utc_now_iso() -> str:
    """
    Return timezone-aware UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# LOGGING
# ============================================================

def log(message: str) -> None:
    """
    Simple deterministic stdout logger.

    We intentionally keep Unit 1 logging small.
    A structured logger can replace this later without
    changing trading logic.
    """

    print(
        f"{utc_now_iso()} {message}",
        flush=True,
    )


def separator() -> None:

    print(
        "-" * 80,
        flush=True,
    )


# ============================================================
# QUANTIZATION
# ============================================================

def quantize_down(
    value: Any,
    step: Any,
) -> Decimal:
    """
    Quantize DOWN to an exchange step.

    Example:

        value = 0.00047
        step  = 0.0001

        result = 0.0004
    """

    value = D(value)
    step = D(step)

    if step <= 0:

        raise ValueError(
            "Quantization step must be greater than zero."
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return units * step


def decimal_to_string(
    value: Any,
) -> str:
    """
    Convert Decimal-compatible value into a plain decimal
    string without scientific notation or unnecessary zeros.
    """

    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:

        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text


# ============================================================
# IMMUTABLE STRATEGY CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class StrategyConfig:

    symbol: str = "BTCUSDT"

    price_step: Decimal = Decimal(
        "0.1"
    )

    quantity_step: Decimal = Decimal(
        "0.0001"
    )

    minimum_quantity: Decimal = Decimal(
        "0.0001"
    )

    entry_margin_percent: Decimal = Decimal(
        "5"
    )

    long_leverage: Decimal = Decimal(
        "100"
    )

    short_leverage: Decimal = Decimal(
        "100"
    )

    margin_mode: str = "ISOLATED"

    pyramid_add_percent: Decimal = Decimal(
        "5"
    )

    max_pyramid_adds: int = 1

    backup_margin_percent: Decimal = Decimal(
        "5"
    )

    backup_buffer_percent: Decimal = Decimal(
        "0.30"
    )

    max_backups: int = 3

    maximum_fund_exposure_percent: Decimal = Decimal(
        "35"
    )

    signal_expiry_seconds: int = 120

    loss_cooldown_seconds: int = 300

    one_direction_only: bool = True

    anti_duplicate_orders: bool = True


# ============================================================
# EMA CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class EMAConfig:

    fast_period: int = 19

    medium_period: int = 50

    slow_period: int = 200

    confirmation_candles: int = 1

    minimum_fast_medium_separation_percent: Decimal = Decimal(
        "0.01"
    )


# ============================================================
# TP CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class TakeProfitConfig:

    tp1_allocation_percent: Decimal = Decimal(
        "20"
    )

    tp2_allocation_percent: Decimal = Decimal(
        "20"
    )

    tp3_allocation_percent: Decimal = Decimal(
        "60"
    )

    tp3_trailing_distance_percent: Decimal = Decimal(
        "0.20"
    )


# ============================================================
# EXECUTION SAFETY CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class ExecutionSafetyConfig:

    """
    IMPORTANT:

    Every mutation capability begins FALSE.

    Later reconstruction units are NOT allowed simply to
    overwrite these values.

    Execution authorization will eventually be implemented
    through a separate explicit execution boundary.
    """

    demo_order_execution: bool = False

    real_order_execution: bool = False

    exchange_mutation_transport: bool = False

    order_submission: bool = False

    leverage_mutation: bool = False

    margin_mode_mutation: bool = False

    position_mutation: bool = False

    first_real_order_allowed: bool = False


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class AppConfig:

    strategy: StrategyConfig

    ema: EMAConfig

    take_profit: TakeProfitConfig

    execution: ExecutionSafetyConfig


def build_config() -> AppConfig:
    """
    Construct the complete immutable Unit 1 configuration.
    """

    return AppConfig(

        strategy=StrategyConfig(),

        ema=EMAConfig(),

        take_profit=TakeProfitConfig(),

        execution=ExecutionSafetyConfig(),

    )


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_strategy_config(
    config: StrategyConfig,
) -> None:

    if not config.symbol:

        raise ValueError(
            "Symbol cannot be empty."
        )

    if config.price_step <= 0:

        raise ValueError(
            "Price step must be positive."
        )

    if config.quantity_step <= 0:

        raise ValueError(
            "Quantity step must be positive."
        )

    if config.minimum_quantity <= 0:

        raise ValueError(
            "Minimum quantity must be positive."
        )

    if config.entry_margin_percent <= 0:

        raise ValueError(
            "Entry margin percent must be positive."
        )

    if config.entry_margin_percent > 100:

        raise ValueError(
            "Entry margin percent cannot exceed 100."
        )

    if config.long_leverage <= 0:

        raise ValueError(
            "Long leverage must be positive."
        )

    if config.short_leverage <= 0:

        raise ValueError(
            "Short leverage must be positive."
        )

    if config.max_pyramid_adds < 0:

        raise ValueError(
            "Maximum pyramid adds cannot be negative."
        )

    if config.max_backups < 0:

        raise ValueError(
            "Maximum backups cannot be negative."
        )

    if config.backup_margin_percent <= 0:

        raise ValueError(
            "Backup margin percent must be positive."
        )

    if config.backup_buffer_percent <= 0:

        raise ValueError(
            "Backup buffer percent must be positive."
        )

    if (
        config.maximum_fund_exposure_percent
        <= 0
    ):

        raise ValueError(
            "Maximum fund exposure must be positive."
        )

    if (
        config.maximum_fund_exposure_percent
        > 100
    ):

        raise ValueError(
            "Maximum fund exposure cannot exceed 100."
        )

    if config.signal_expiry_seconds <= 0:

        raise ValueError(
            "Signal expiry must be positive."
        )

    if config.loss_cooldown_seconds < 0:

        raise ValueError(
            "Loss cooldown cannot be negative."
        )


def validate_ema_config(
    config: EMAConfig,
) -> None:

    if config.fast_period <= 0:

        raise ValueError(
            "Fast EMA period must be positive."
        )

    if config.medium_period <= 0:

        raise ValueError(
            "Medium EMA period must be positive."
        )

    if config.slow_period <= 0:

        raise ValueError(
            "Slow EMA period must be positive."
        )

    if not (
        config.fast_period
        < config.medium_period
        < config.slow_period
    ):

        raise ValueError(
            "EMA periods must satisfy FAST < MEDIUM < SLOW."
        )

    if config.confirmation_candles <= 0:

        raise ValueError(
            "EMA confirmation candles must be positive."
        )

    if (
        config.minimum_fast_medium_separation_percent
        < 0
    ):

        raise ValueError(
            "EMA separation cannot be negative."
        )


def validate_take_profit_config(
    config: TakeProfitConfig,
) -> None:

    allocations = (

        config.tp1_allocation_percent
        + config.tp2_allocation_percent
        + config.tp3_allocation_percent

    )

    if allocations != Decimal("100"):

        raise ValueError(
            "TP allocations must total exactly 100 percent."
        )

    if (
        config.tp3_trailing_distance_percent
        <= 0
    ):

        raise ValueError(
            "TP3 trailing distance must be positive."
        )


# ============================================================
# HARD EXECUTION FIREBREAK
# ============================================================

def validate_execution_firebreak(
    config: ExecutionSafetyConfig,
) -> None:
    """
    Unit 1 MUST fail immediately if any exchange mutation
    capability is enabled.

    This prevents future reconstruction work from accidentally
    inheriting a writable execution state.
    """

    mutation_flags = {

        "demo_order_execution":
            config.demo_order_execution,

        "real_order_execution":
            config.real_order_execution,

        "exchange_mutation_transport":
            config.exchange_mutation_transport,

        "order_submission":
            config.order_submission,

        "leverage_mutation":
            config.leverage_mutation,

        "margin_mode_mutation":
            config.margin_mode_mutation,

        "position_mutation":
            config.position_mutation,

        "first_real_order_allowed":
            config.first_real_order_allowed,

    }

    enabled = [

        name

        for name, state
        in mutation_flags.items()

        if state is True

    ]

    if enabled:

        raise RuntimeError(

            "EXECUTION FIREBREAK VIOLATION: "
            + ", ".join(enabled)

        )


# ============================================================
# COMPLETE CONFIG VALIDATION
# ============================================================

def validate_config(
    config: AppConfig,
) -> None:

    validate_strategy_config(
        config.strategy
    )

    validate_ema_config(
        config.ema
    )

    validate_take_profit_config(
        config.take_profit
    )

    validate_execution_firebreak(
        config.execution
    )


# ============================================================
# ENVIRONMENT INSPECTION
# ============================================================

def inspect_environment() -> dict:
    """
    Unit 1 does NOT require WEEX credentials.

    We only report whether credential variables exist.

    Their values are NEVER printed.
    """

    names = (

        "WEEX_API_KEY",

        "WEEX_API_SECRET",

        "WEEX_API_PASSPHRASE",

        "TELEGRAM_BOT_TOKEN",

        "TELEGRAM_CHAT_ID",

    )

    return {

        name: bool(
            os.getenv(
                name,
                ""
            ).strip()
        )

        for name in names

    }


# ============================================================
# SELF-TEST FRAMEWORK
# ============================================================

class UnitTestFailure(
    RuntimeError
):
    pass


def assert_equal(
    name: str,
    actual: Any,
    expected: Any,
) -> None:

    if actual != expected:

        raise UnitTestFailure(

            f"{name}: "
            f"expected={expected!r} "
            f"actual={actual!r}"

        )

    log(
        f"PASS: {name}"
    )


def assert_true(
    name: str,
    condition: bool,
) -> None:

    if not condition:

        raise UnitTestFailure(
            f"{name}: condition was False"
        )

    log(
        f"PASS: {name}"
    )


# ============================================================
# UNIT 1 SELF TEST
# ============================================================

def run_unit_1_self_test() -> bool:

    separator()

    log(
        "RECONSTRUCTION UNIT 1 SELF-TEST START"
    )

    separator()

    config = build_config()

    # --------------------------------------------------------
    # TEST 1
    # Complete configuration validates.
    # --------------------------------------------------------

    validate_config(
        config
    )

    log(
        "PASS: COMPLETE CONFIG VALIDATION"
    )

    # --------------------------------------------------------
    # TEST 2
    # Symbol.
    # --------------------------------------------------------

    assert_equal(

        "SYMBOL",

        config.strategy.symbol,

        "BTCUSDT",

    )

    # --------------------------------------------------------
    # TEST 3
    # Exchange price step.
    # --------------------------------------------------------

    assert_equal(

        "PRICE STEP",

        config.strategy.price_step,

        Decimal("0.1"),

    )

    # --------------------------------------------------------
    # TEST 4
    # Exchange quantity step.
    # --------------------------------------------------------

    assert_equal(

        "QUANTITY STEP",

        config.strategy.quantity_step,

        Decimal("0.0001"),

    )

    # --------------------------------------------------------
    # TEST 5
    # Minimum quantity.
    # --------------------------------------------------------

    assert_equal(

        "MINIMUM QUANTITY",

        config.strategy.minimum_quantity,

        Decimal("0.0001"),

    )

    # --------------------------------------------------------
    # TEST 6
    # Entry allocation.
    # --------------------------------------------------------

    assert_equal(

        "ENTRY MARGIN PERCENT",

        config.strategy.entry_margin_percent,

        Decimal("5"),

    )

    # --------------------------------------------------------
    # TEST 7
    # Leverage configuration.
    # --------------------------------------------------------

    assert_equal(

        "LONG LEVERAGE",

        config.strategy.long_leverage,

        Decimal("100"),

    )

    assert_equal(

        "SHORT LEVERAGE",

        config.strategy.short_leverage,

        Decimal("100"),

    )

    # --------------------------------------------------------
    # TEST 8
    # Backup configuration.
    # --------------------------------------------------------

    assert_equal(

        "MAX BACKUPS",

        config.strategy.max_backups,

        3,

    )

    assert_equal(

        "BACKUP MARGIN PERCENT",

        config.strategy.backup_margin_percent,

        Decimal("5"),

    )

    assert_equal(

        "BACKUP BUFFER PERCENT",

        config.strategy.backup_buffer_percent,

        Decimal("0.30"),

    )

    # --------------------------------------------------------
    # TEST 9
    # Exposure ceiling.
    # --------------------------------------------------------

    assert_equal(

        "MAXIMUM FUND EXPOSURE",

        config.strategy.maximum_fund_exposure_percent,

        Decimal("35"),

    )

    # --------------------------------------------------------
    # TEST 10
    # EMA configuration.
    # --------------------------------------------------------

    assert_equal(

        "EMA FAST",

        config.ema.fast_period,

        19,

    )

    assert_equal(

        "EMA MEDIUM",

        config.ema.medium_period,

        50,

    )

    assert_equal(

        "EMA SLOW",

        config.ema.slow_period,

        200,

    )

    # --------------------------------------------------------
    # TEST 11
    # TP allocation.
    # --------------------------------------------------------

    total_tp_allocation = (

        config.take_profit.tp1_allocation_percent
        + config.take_profit.tp2_allocation_percent
        + config.take_profit.tp3_allocation_percent

    )

    assert_equal(

        "TP ALLOCATION TOTAL",

        total_tp_allocation,

        Decimal("100"),

    )

    # --------------------------------------------------------
    # TEST 12
    # Decimal quantization.
    # --------------------------------------------------------

    quantized_quantity = quantize_down(

        Decimal("0.00047"),

        config.strategy.quantity_step,

    )

    assert_equal(

        "QUANTITY QUANTIZATION",

        quantized_quantity,

        Decimal("0.0004"),

    )

    quantized_price = quantize_down(

        Decimal("83941.57"),

        config.strategy.price_step,

    )

    assert_equal(

        "PRICE QUANTIZATION",

        quantized_price,

        Decimal("83941.5"),

    )

    # --------------------------------------------------------
    # TEST 13
    # Decimal serialization.
    # --------------------------------------------------------

    assert_equal(

        "DECIMAL STRING",

        decimal_to_string(
            Decimal("0.0004000")
        ),

        "0.0004",

    )

    # --------------------------------------------------------
    # TEST 14
    # Hard execution firebreak.
    # --------------------------------------------------------

    assert_true(

        "DEMO EXECUTION DISABLED",

        config.execution.demo_order_execution
        is False,

    )

    assert_true(

        "REAL EXECUTION DISABLED",

        config.execution.real_order_execution
        is False,

    )

    assert_true(

        "EXCHANGE MUTATION TRANSPORT DISABLED",

        config.execution.exchange_mutation_transport
        is False,

    )

    assert_true(

        "ORDER SUBMISSION DISABLED",

        config.execution.order_submission
        is False,

    )

    assert_true(

        "LEVERAGE MUTATION DISABLED",

        config.execution.leverage_mutation
        is False,

    )

    assert_true(

        "MARGIN MODE MUTATION DISABLED",

        config.execution.margin_mode_mutation
        is False,

    )

    assert_true(

        "POSITION MUTATION DISABLED",

        config.execution.position_mutation
        is False,

    )

    assert_true(

        "FIRST REAL ORDER DISABLED",

        config.execution.first_real_order_allowed
        is False,

    )

    # --------------------------------------------------------
    # TE
