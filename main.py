
#!/usr/bin/env python3

"""
WEEX PARALLEL BOT RECONSTRUCTION

UNIT 4
REGIME / DIRECTION CLASSIFICATION ENGINE

BUILDS ON:
    UNIT 1 - FOUNDATION / SAFETY
    UNIT 2 - READ-ONLY WEEX TRANSPORT
    UNIT 3 - CANDLE + EMA ENGINE

ADDS:
    UNIT 4 - REGIME / DIRECTION CLASSIFICATION

SAFETY:
    GET ONLY
    NO POST FUNCTION
    NO DEMO ORDER
    NO REAL ORDER
    NO EXCHANGE MUTATION
    NO ORDER PAYLOAD
"""

import asyncio
import aiohttp
import base64
import hashlib
import hmac
import json
import os
import time

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_DOWN
from typing import Any
from urllib.parse import urlencode


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "WEEX_PARALLEL_BOT"

APP_VERSION = "0.4.0"

RECONSTRUCTION_UNIT = "UNIT_4_REGIME_DIRECTION_ENGINE"


# ============================================================
# WEEX CONFIG
# ============================================================

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = "BTCUSDT"

PUBLIC_TICKER_SYMBOL = "cmt_btcusdt"

KLINE_SYMBOL = "cmt_btcusdt"

KLINE_INTERVAL = "1m"

HISTORICAL_LIMIT = 250


# ============================================================
# DECIMAL
# ============================================================

def D(value: Any) -> Decimal:

    return Decimal(
        str(value)
    )


def decimal_to_string(
    value: Any,
) -> str:

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


def quantize_down(
    value: Any,
    step: Any,
) -> Decimal:

    value = D(value)

    step = D(step)

    if step <= 0:

        raise ValueError(
            "Step must be positive."
        )

    units = (
        value / step
    ).to_integral_value(
        rounding=ROUND_DOWN
    )

    return (
        units * step
    )


# ============================================================
# TIME / LOGGING
# ============================================================

def utc_now_iso() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def log(
    message: str,
) -> None:

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
# CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class StrategyConfig:

    symbol: str = SYMBOL

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


@dataclass(
    frozen=True
)
class ExecutionSafetyConfig:

    demo_order_execution: bool = False

    real_order_execution: bool = False

    exchange_mutation_transport: bool = False

    order_submission: bool = False

    leverage_mutation: bool = False

    margin_mode_mutation: bool = False

    position_mutation: bool = False

    first_real_order_allowed: bool = False


@dataclass(
    frozen=True
)
class AppConfig:

    strategy: StrategyConfig

    ema: EMAConfig

    take_profit: TakeProfitConfig

    execution: ExecutionSafetyConfig


def build_config() -> AppConfig:

    return AppConfig(

        strategy=StrategyConfig(),

        ema=EMAConfig(),

        take_profit=TakeProfitConfig(),

        execution=ExecutionSafetyConfig(),

    )


# ============================================================
# CONFIG VALIDATION
# ============================================================

def validate_config(
    config: AppConfig,
) -> None:

    strategy = config.strategy

    ema = config.ema

    tp = config.take_profit

    execution = config.execution


    if strategy.price_step <= 0:

        raise ValueError(
            "Invalid price step."
        )


    if strategy.quantity_step <= 0:

        raise ValueError(
            "Invalid quantity step."
        )


    if strategy.minimum_quantity <= 0:

        raise ValueError(
            "Invalid minimum quantity."
        )


    if not (
        0
        < ema.fast_period
        < ema.medium_period
        < ema.slow_period
    ):

        raise ValueError(
            "EMA periods invalid."
        )


    total_tp = (

        tp.tp1_allocation_percent
        + tp.tp2_allocation_percent
        + tp.tp3_allocation_percent

    )


    if total_tp != Decimal("100"):

        raise ValueError(
            "TP allocations must total 100."
        )


    mutation_flags = {

        "demo_order_execution":
            execution.demo_order_execution,

        "real_order_execution":
            execution.real_order_execution,

        "exchange_mutation_transport":
            execution.exchange_mutation_transport,

        "order_submission":
            execution.order_submission,

        "leverage_mutation":
            execution.leverage_mutation,

        "margin_mode_mutation":
            execution.margin_mode_mutation,

        "position_mutation":
            execution.position_mutation,

        "first_real_order_allowed":
            execution.first_real_order_allowed,

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
# READ-ONLY CLIENT
# ============================================================

class ReadOnlyWeexClient:

    """
    GET-only WEEX transport.

    Intentionally provides no POST/PUT/PATCH/DELETE method.
    """

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout_seconds: int = 20,
    ):

        self.base_url = (
            base_url.rstrip("/")
        )

        self.timeout_seconds = (
            timeout_seconds
        )


    async def get(
        self,
        path: str,
        *,
        params: dict | None = None,
    ) -> Any:

        if not path.startswith("/"):

            raise ValueError(
                "Path must begin with '/'."
            )


        params = (
            params
            or {}
        )


        query = urlencode(
            params,
            doseq=True,
        )


        request_target = path


        if query:

            request_target += (
                "?"
                + query
            )


        url = (
            self.base_url
            + request_target
        )


        timeout = aiohttp.ClientTimeout(
            total=self.timeout_seconds
        )


        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url
            ) as response:

                text = (
                    await response.text()
                )


                if response.status >= 400:

                    raise RuntimeError(

                        "WEEX GET FAILED "
                        f"status={response.status} "
                        f"path={path} "
                        f"response={text[:500]}"

                    )


                try:

                    return json.loads(
                        text
                    )

                except json.JSONDecodeError:

                    raise RuntimeError(

                        "WEEX returned non-JSON response "
                        f"path={path} "
                        f"response={text[:500]}"

                    )


# ============================================================
# CANDLE MODEL
# ============================================================

@dataclass(
    frozen=True
)
class Candle:

    timestamp: int

    open: Decimal

    high: Decimal

    low: Decimal

    close: Decimal

    volume: Decimal


# ============================================================
# CANDLE VALIDATION
# ============================================================

def validate_candle(
    candle: Candle,
) -> None:

    if candle.timestamp <= 0:

        raise ValueError(
            "Invalid candle timestamp."
        )


    if candle.open <= 0:

        raise ValueError(
            "Invalid candle open."
        )


    if candle.high <= 0:

        raise ValueError(
            "Invalid candle high."
        )


    if candle.low <= 0:

        raise ValueError(
            "Invalid candle low."
        )


    if candle.close <= 0:

        raise ValueError(
            "Invalid candle close."
        )


    if candle.volume < 0:

        raise ValueError(
            "Invalid candle volume."
        )


    highest_body_price = max(
        candle.open,
        candle.close,
    )


    lowest_body_price = min(
        candle.open,
        candle.close,
    )


    if candle.high < highest_body_price:

        raise ValueError(
            "Candle high below body."
        )


    if candle.low > lowest_body_price:

        raise ValueError(
            "Candle low above body."
        )


    if candle.high < candle.low:

        raise ValueError(
            "Candle high below candle low."
        )


# ============================================================
# RAW CANDLE PARSER
# ============================================================

def parse_candle_row(
    row: Any,
) -> Candle | None:

    """
    Supports both common exchange formats:

    list:
        [timestamp, open, high, low, close, volume, ...]

    dict:
        {
            timestamp/time: ...,
            open: ...,
            high: ...,
            low: ...,
            close: ...,
            volume: ...
        }
    """


    try:

        if isinstance(
            row,
            (list, tuple),
        ):

            if len(row) < 6:

                return None


            candle = Candle(

                timestamp=int(
                    D(
                        row[0]
                    )
                ),

                open=D(
                    row[1]
                ),

                high=D(
                    row[2]
                ),

                low=D(
                    row[3]
                ),

                close=D(
                    row[4]
                ),

                volume=D(
                    row[5]
                ),

            )


        elif isinstance(
            row,
            dict,
        ):

            timestamp = (

                row.get(
                    "timestamp"
                )

                or row.get(
                    "time"
                )

                or row.get(
                    "ts"
                )

                or row.get(
                    "t"
                )

            )


            open_price = (

                row.get(
                    "open"
                )

                or row.get(
                    "o"
                )

            )


            high_price = (

                row.get(
                    "high"
                )

                or row.get(
                    "h"
                )

            )


            low_price = (

                row.get(
                    "low"
                )

                or row.get(
                    "l"
                )

            )


            close_price = (

                row.get(
                    "close"
                )

                or row.get(
                    "c"
                )

            )


            volume = (

                row.get(
                    "volume"
                )

                or row.get(
                    "vol"
                )

                or row.get(
                    "v"
                )

                or "0"

            )


            if any(

                value is None

                for value in (

                    timestamp,
                    open_price,
                    high_price,
                    low_price,
                    close_price,

                )

            ):

                return None


            candle = Candle(

                timestamp=int(
                    D(
                        timestamp
                    )
                ),

                open=D(
                    open_price
                ),

                high=D(
                    high_price
                ),

                low=D(
                    low_price
                ),

                close=D(
                    close_price
                ),

                volume=D(
                    volume
                ),

            )


        else:

            return None


        validate_candle(
            candle
        )


        return candle


    except Exception:

        return None


# ============================================================
# EXTRACT CANDLE ROWS
# ============================================================

def extract_candle_rows(
    payload: Any,
) -> list:

    if isinstance(
        payload,
        list,
    ):

        return payload


    if not isinstance(
        payload,
        dict,
    ):

        return []


    for key in (

        "data",
        "list",
        "rows",
        "result",

    ):

        value = payload.get(
            key
        )


        if isinstance(
            value,
            list,
        ):

            return value


        if isinstance(
            value,
            dict,
        ):

            nested = extract_candle_rows(
                value
            )


            if nested:

                return nested


    return []


# ============================================================
# NORMALIZE CANDLES
# ============================================================

def normalize_candles(
    payload: Any,
) -> list[Candle]:

    rows = extract_candle_rows(
        payload
    )


    candles = []


    for row in rows:

        candle = parse_candle_row(
            row
        )


        if candle is not None:

            candles.append(
                candle
            )


    unique = {

        candle.timestamp:
            candle

        for candle in candles

    }


    candles = list(
        unique.values()
    )


    candles.sort(
        key=lambda item:
            item.timestamp
    )


    return candles


# ============================================================
# CANDLE SERIES VALIDATION
# ============================================================

def validate_candle_series(
    candles: list[Candle],
    *,
    minimum_count: int,
) -> None:

    if len(candles) < minimum_count:

        raise ValueError(

            "Insufficient candle history: "
            f"need={minimum_count} "
            f"received={len(candles)}"

        )


    previous_timestamp = None


    for candle in candles:

        validate_candle(
            candle
        )


        if previous_timestamp is not None:

            if (
                candle.timestamp
                <= previous_timestamp
            ):

                raise ValueError(
                    "Candles are not strictly chronological."
                )


        previous_timestamp = (
            candle.timestamp
        )


# ============================================================
# EMA
# ============================================================

def calculate_ema_series(
    values: list[Decimal],
    period: int,
) -> list[Decimal]:

    """
    Standard EMA calculation.

    Seed:
        SMA of first `period` values.

    Thereafter:
        EMA =
            price * multiplier
            + previous_ema * (1 - multiplier)

    multiplier:
        2 / (period + 1)
    """


    if period <= 0:

        raise ValueError(
            "EMA period must be positive."
        )


    if len(values) < period:

        raise ValueError(

            "Insufficient values for EMA "
            f"period={period} "
            f"values={len(values)}"

        )


    decimal_period = Decimal(
        period
    )


    seed = (

        sum(
            values[:period],
            Decimal("0"),
        )

        / decimal_period

    )


    multiplier = (

        Decimal("2")

        / Decimal(
            period + 1
        )

    )


    result = [
        seed
    ]


    previous = seed


    for price in values[
        period:
    ]:

        current = (

            (
                price
                * multiplier
            )

            +

            (
                previous
                * (
                    Decimal("1")
                    - multiplier
                )
            )

        )


        result.append(
            current
        )


        previous = current


    return result


def calculate_latest_ema(
    values: list[Decimal],
    period: int,
) -> Decimal:

    series = calculate_ema_series(
        values,
        period,
    )


    return series[
        -1
    ]


# ============================================================
# EMA SNAPSHOT
# ============================================================

@dataclass(
    frozen=True
)
class EMASnapshot:

    candle_timestamp: int

    close_price: Decimal

    ema_fast: Decimal

    ema_medium: Decimal

    ema_slow: Decimal

    fast_medium_separation_percent: Decimal

    medium_slow_separation_percent: Decimal

    fast_slow_separation_percent: Decimal

    alignment: str


# ============================================================
# PERCENTAGE DISTANCE
# ============================================================

def percentage_distance(
    first: Decimal,
    second: Decimal,
) -> Decimal:

    if second == 0:

        raise ValueError(
            "Cannot calculate percentage distance from zero."
        )


    return (

        abs(
            first - second
        )

        / abs(
            second
        )

        * Decimal("100")

    )


# ============================================================
# EMA ALIGNMENT
# ============================================================

def determine_ema_alignment(
    fast: Decimal,
    medium: Decimal,
    slow: Decimal,
) -> str:

    if (
        fast
        > medium
        > slow
    ):

        return "BULLISH"


    if (
        fast
        < medium
        < slow
    ):

        return "BEARISH"


    return "MIXED"


# ============================================================
# BUILD EMA SNAPSHOT
# ============================================================

def build_ema_snapshot(
    candles: list[Candle],
    config: EMAConfig,
) -> EMASnapshot:

    validate_candle_series(

        candles,

        minimum_count=config.slow_period,

    )


    closes = [

        candle.close

        for candle in candles

    ]


    fast = calculate_latest_ema(

        closes,

        config.fast_period,

    )


    medium = calculate_latest_ema(

        closes,

        config.medium_period,

    )


    slow = calculate_latest_ema(

        closes,

        config.slow_period,

    )


    fast_medium = percentage_distance(
        fast,
        medium,
    )


    medium_slow = percentage_distance(
        medium,
        slow,
    )


    fast_slow = percentage_distance(
        fast,
        slow,
    )


    alignment = determine_ema_alignment(
        fast,
        medium,
        slow,
    )


    latest = candles[
        -1
    ]


    return EMASnapshot(

        candle_timestamp=
            latest.timestamp,

        close_price=
            latest.close,

        ema_fast=
            fast,

        ema_medium=
            medium,

        ema_slow=
            slow,

        fast_medium_separation_percent=
            fast_medium,

        medium_slow_separation_percent=
            medium_slow,

        fast_slow_separation_percent=
            fast_slow,

        alignment=
            alignment,

    )


# ============================================================
# END PART 1 OF 2
# PART 2 STARTS WITH:
# DETERMINISTIC SYNTHETIC CANDLES
# ============================================================
