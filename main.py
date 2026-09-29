#!/usr/bin/env python3

"""
WEEX PARALLEL BOT RECONSTRUCTION

UNIT 4 MERGED
MARKET DATA + CANDLE NORMALIZATION + EMA ENGINE
+ REGIME / DIRECTION ENGINE

BUILDS ON:
    UNIT 1 - FOUNDATION / SAFETY
    UNIT 2 - READ-ONLY WEEX TRANSPORT
    UNIT 3 - CANDLE + EMA ENGINE

ADDS:
    UNIT 4 - REGIME + DIRECTION ENGINE

SAFETY:
    GET ONLY
    NO POST FUNCTION
    NO DEMO ORDER
    NO REAL ORDER
    NO EXCHANGE MUTATION
    NO ORDER PAYLOAD

UNIT 4 OBJECTIVES
-----------------
1. Preserve verified Unit 1-3 behavior.
2. Determine LONG / SHORT / NONE from EMA ordering.
3. Classify SCALP / STRUCTURE / BREAKOUT.
4. Preserve verified 0.05% strong EMA separation.
5. Preserve verified 0.60% breakout movement.
6. Require three confirmations for mode transitions.
7. Preserve active-trade mode lock behavior.
8. Generate classification only.
9. Generate no exchange order.
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

RECONSTRUCTION_UNIT = "UNIT_4_MERGED_REGIME_DIRECTION_ENGINE"


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


    # --------------------------------------------------------
    # Deduplicate by timestamp.
    # --------------------------------------------------------

    unique = {

        candle.timestamp:
            candle

        for candle in candles

    }


    candles = list(
        unique.values()
    )


    # --------------------------------------------------------
    # WEEX may return newest-first.
    #
    # Internal representation is ALWAYS oldest -> newest.
    # --------------------------------------------------------

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
# DETERMINISTIC SYNTHETIC CANDLES
# ============================================================

def build_synthetic_candles(
    *,
    count: int,
    starting_price: Decimal,
    increment: Decimal,
) -> list[Candle]:

    if count <= 0:

        raise ValueError(
            "Synthetic count must be positive."
        )


    candles = []


    timestamp = 1_700_000_000_000


    price = starting_price


    for index in range(
        count
    ):

        close = (

            price

            + (
                increment
                * Decimal(index)
            )

        )


        open_price = (
            close
            - Decimal("0.5")
        )


        high = (
            max(
                open_price,
                close,
            )
            + Decimal("1")
        )


        low = (
            min(
                open_price,
                close,
            )
            - Decimal("1")
        )


        candles.append(

            Candle(

                timestamp=(
                    timestamp
                    + (
                        index
                        * 60_000
                    )
                ),

                open=open_price,

                high=high,

                low=low,

                close=close,

                volume=Decimal("10"),

            )

        )


    return candles


# ============================================================
# LOCAL EMA TESTS
# ============================================================

def run_local_ema_tests(
    config: EMAConfig,
) -> None:

    separator()

    log(
        "UNIT 3 LOCAL EMA TESTS START"
    )


    # --------------------------------------------------------
    # TEST 1:
    # Constant price must produce identical EMA values.
    # --------------------------------------------------------

    constant_candles = (
        build_synthetic_candles(

            count=250,

            starting_price=
                Decimal("100"),

            increment=
                Decimal("0"),

        )
    )


    constant_snapshot = (
        build_ema_snapshot(

            constant_candles,

            config,

        )
    )


    if (
        constant_snapshot.ema_fast
        != Decimal("100")
    ):

        raise RuntimeError(
            "Constant EMA19 test failed."
        )


    if (
        constant_snapshot.ema_medium
        != Decimal("100")
    ):

        raise RuntimeError(
            "Constant EMA50 test failed."
        )


    if (
        constant_snapshot.ema_slow
        != Decimal("100")
    ):

        raise RuntimeError(
            "Constant EMA200 test failed."
        )


    if (
        constant_snapshot.alignment
        != "MIXED"
    ):

        raise RuntimeError(
            "Constant alignment test failed."
        )


    log(
        "PASS: CONSTANT PRICE EMA TEST"
    )


    # --------------------------------------------------------
    # TEST 2:
    # Rising market should produce:
    # EMA19 > EMA50 > EMA200
    # --------------------------------------------------------

    rising_candles = (
        build_synthetic_candles(

            count=250,

            starting_price=
                Decimal("100"),

            increment=
                Decimal("1"),

        )
    )


    rising_snapshot = (
        build_ema_snapshot(

            rising_candles,

            config,

        )
    )


    if not (

        rising_snapshot.ema_fast

        >

        rising_snapshot.ema_medium

        >

        rising_snapshot.ema_slow

    ):

        raise RuntimeError(
            "Rising EMA ordering failed."
        )


    if (
        rising_snapshot.alignment
        != "BULLISH"
    ):

        raise RuntimeError(
            "Rising alignment failed."
        )


    log(
        "PASS: RISING MARKET EMA TEST"
    )


    # --------------------------------------------------------
    # TEST 3:
    # Falling market should produce:
    # EMA19 < EMA50 < EMA200
    # --------------------------------------------------------

    falling_candles = (
        build_synthetic_candles(

            count=250,

            starting_price=
                Decimal("500"),

            increment=
                Decimal("-1"),

        )
    )


    falling_snapshot = (
        build_ema_snapshot(

            falling_candles,

            config,

        )
    )


    if not (

        falling_snapshot.ema_fast

        <

        falling_snapshot.ema_medium

        <

        falling_snapshot.ema_slow

    ):

        raise RuntimeError(
            "Falling EMA ordering failed."
        )


    if (
        falling_snapshot.alignment
        != "BEARISH"
    ):

        raise RuntimeError(
            "Falling alignment failed."
        )


    log(
        "PASS: FALLING MARKET EMA TEST"
    )


    # --------------------------------------------------------
    # TEST 4:
    # Insufficient history MUST fail.
    # --------------------------------------------------------

    rejected = False


    try:

        build_ema_snapshot(

            rising_candles[:100],

            config,

        )


    except ValueError:

        rejected = True


    if not rejected:

        raise RuntimeError(
            "Insufficient-history rejection failed."
        )


    log(
        "PASS: INSUFFICIENT HISTORY REJECTED"
    )


    # --------------------------------------------------------
    # TEST 5:
    # Malformed candle MUST fail validation.
    # --------------------------------------------------------

    malformed = Candle(

        timestamp=1,

        open=Decimal("100"),

        high=Decimal("90"),

        low=Decimal("80"),

        close=Decimal("100"),

        volume=Decimal("1"),

    )


    rejected = False


    try:

        validate_candle(
            malformed
        )


    except ValueError:

        rejected = True


    if not rejected:

        raise RuntimeError(
            "Malformed candle rejection failed."
        )


    log(
        "PASS: MALFORMED CANDLE REJECTED"
    )


    separator()

    log(
        "UNIT 3 LOCAL EMA TESTS = PASS"
    )


# ============================================================
# PUBLIC TICKER PRICE
# ============================================================

def find_price(
    payload: Any,
) -> Decimal | None:

    price_keys = (

        "markPrice",
        "last",
        "lastPrice",
        "close",
        "price",

    )


    if isinstance(
        payload,
        dict,
    ):

        for key in price_keys:

            raw = payload.get(
                key
            )


            if raw not in (
                None,
                "",
            ):

                try:

                    price = D(
                        raw
                    )


                    if price > 0:

                        return price


                except Exception:

                    pass


        for value in payload.values():

            if isinstance(
                value,
                (dict, list),
            ):

                result = find_price(
                    value
                )


                if result is not None:

                    return result


    elif isinstance(
        payload,
        list,
    ):

        for value in payload:

            result = find_price(
                value
            )


            if result is not None:

                return result


    return None


async def load_public_price(
    client: ReadOnlyWeexClient,
) -> Decimal:

    payload = await client.get(

        "/capi/v2/market/ticker",

        params={

            "symbol":
                PUBLIC_TICKER_SYMBOL,

        },

    )


    price = find_price(
        payload
    )


    if (
        price is None
        or price <= 0
    ):

        raise RuntimeError(
            "Unable to extract public BTC price."
        )


    return price


# ============================================================
# KLINE REQUEST CANDIDATES
# ============================================================

async def load_live_candles(
    client: ReadOnlyWeexClient,
) -> tuple[list[Candle], str]:

    """
    Keep endpoint compatibility isolated here.

    The first successful response producing >= EMA200 candles
    is selected.

    No strategy code knows or cares which exchange adapter
    endpoint produced them.
    """


    candidate_requests = (

        (
            "/capi/v2/market/candles",
            {

                "symbol":
                    KLINE_SYMBOL,

                "granularity":
                    KLINE_INTERVAL,

                "limit":
                    str(
                        HISTORICAL_LIMIT
                    ),

            },
        ),

        (
            "/capi/v2/market/kline",
            {

                "symbol":
                    KLINE_SYMBOL,

                "interval":
                    KLINE_INTERVAL,

                "limit":
                    str(
                        HISTORICAL_LIMIT
                    ),

            },
        ),

        (
            "/capi/v2/market/klines",
            {

                "symbol":
                    KLINE_SYMBOL,

                "interval":
                    KLINE_INTERVAL,

                "limit":
                    str(
                        HISTORICAL_LIMIT
                    ),

            },
        ),

    )


    failures = []


    for (
        path,
        params,
    ) in candidate_requests:

        try:

            payload = await client.get(

                path,

                params=params,

            )


            candles = normalize_candles(
                payload
            )


            if len(candles) >= 200:

                return (
                    candles,
                    path,
                )


            failures.append(

                f"{path}: "
                f"only {len(candles)} valid candles"

            )


        except Exception as exc:

            failures.append(

                f"{path}: "
                f"{type(exc).__name__}: "
                f"{exc}"

            )


    raise RuntimeError(

        "NO VALID WEEX KLINE SOURCE: "
        + " | ".join(
            failures
        )

    )


# ============================================================
# UNIT 4 REGIME CONFIGURATION
# ============================================================

@dataclass(
    frozen=True
)
class RegimeConfig:

    strong_ema_separation_percent: Decimal = Decimal(
        "0.05"
    )

    breakout_move_percent: Decimal = Decimal(
        "0.60"
    )

    mode_confirmations_required: int = 3

    exclusive_mode: bool = True

    active_trade_mode_lock: bool = True


# ============================================================
# UNIT 4 REGIME STATE
# ============================================================

@dataclass
class RegimeState:

    active_mode: str | None = None

    pending_mode: str | None = None

    pending_count: int = 0

    mode_locked: bool = False

    last_direction: str | None = None

    last_reason: str | None = None

    cycle: int = 0

    reference_price: Decimal | None = None


# ============================================================
# UNIT 4 REGIME RESULT
# ============================================================

@dataclass(
    frozen=True
)
class RegimeResult:

    cycle: int

    raw_mode: str

    active_mode: str

    direction: str | None

    ema_separation_percent: Decimal

    short_term_move_percent: Decimal

    pending_mode: str | None

    pending_count: int

    mode_locked: bool

    reason: str

    real_execution: bool = False

    demo_execution: bool = False

    write_transport: bool = False


# ============================================================
# UNIT 4 DIRECTION FROM EMA
# ============================================================

def determine_direction_from_ema(
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
) -> str | None:

    if (
        ema19
        > ema50
        > ema200
    ):

        return "LONG"


    if (
        ema19
        < ema50
        < ema200
    ):

        return "SHORT"


    return None


# ============================================================
# UNIT 4 SHORT-TERM MOVEMENT
# ============================================================

def calculate_move_percent(
    current_price: Decimal,
    reference_price: Decimal,
) -> Decimal:

    current_price = D(
        current_price
    )

    reference_price = D(
        reference_price
    )


    if reference_price == 0:

        return Decimal("0")


    return (

        abs(
            current_price
            - reference_price
        )

        / abs(
            reference_price
        )

        * Decimal("100")

    )


# ============================================================
# UNIT 4 RAW REGIME CLASSIFIER
# ============================================================

def classify_raw_regime(
    *,
    direction: str | None,
    ema_separation_percent: Decimal,
    short_term_move_percent: Decimal,
    config: RegimeConfig,
) -> tuple[str, str]:

    direction_valid = (
        direction
        in (
            "LONG",
            "SHORT",
        )
    )


    if (
        direction_valid
        and
        short_term_move_percent
        >=
        config.breakout_move_percent
    ):

        return (
            "BREAKOUT",
            "BREAKOUT_MOVE_CONFIRMED",
        )


    if (
        direction_valid
        and
        ema_separation_percent
        >=
        config.strong_ema_separation_percent
    ):

        return (
            "STRUCTURE",
            "STRONG_EMA_DIRECTION_CONFIRMED",
        )


    return (
        "SCALP",
        "SCALP_DEFAULT",
    )


# ============================================================
# UNIT 4 MODE TRANSITION
# ============================================================

def update_active_mode(
    *,
    state: RegimeState,
    raw_mode: str,
    reason: str,
    trade_active: bool,
    config: RegimeConfig,
) -> str:

    valid_modes = (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    )


    if raw_mode not in valid_modes:

        raise ValueError(
            "Invalid raw regime mode."
        )


    if (
        trade_active
        and
        config.active_trade_mode_lock
        and
        state.active_mode
        in valid_modes
    ):

        state.mode_locked = True

        state.pending_mode = None

        state.pending_count = 0

        state.last_reason = (
            "ACTIVE_TRADE_MODE_LOCK:"
            + str(reason)
        )

        return state.active_mode


    state.mode_locked = False


    if state.active_mode is None:

        state.active_mode = raw_mode

        state.pending_mode = None

        state.pending_count = 0

        state.last_reason = (
            "INITIAL_MODE_ACTIVATED:"
            + str(reason)
        )

        return state.active_mode


    if raw_mode == state.active_mode:

        state.pending_mode = None

        state.pending_count = 0

        state.last_reason = (
            "ACTIVE_MODE_CONFIRMED:"
            + str(reason)
        )

        return state.active_mode


    if state.pending_mode != raw_mode:

        state.pending_mode = raw_mode

        state.pending_count = 1

        state.last_reason = (
            "NEW_MODE_PENDING:"
            + str(reason)
        )

        return state.active_mode


    state.pending_count += 1


    if (
        state.pending_count
        >=
        config.mode_confirmations_required
    ):

        previous_mode = (
            state.active_mode
        )

        state.active_mode = raw_mode

        state.pending_mode = None

        state.pending_count = 0

        state.last_reason = (

            "THREE_CONFIRMATION_TRANSITION:"
            + str(previous_mode)
            + "_TO_"
            + str(raw_mode)

        )

        return state.active_mode


    state.last_reason = (
        "MODE_CONFIRMATION_PENDING:"
        + str(reason)
    )


    return state.active_mode


# ============================================================
# UNIT 4 MERGED CLASSIFICATION CYCLE
# ============================================================

def run_regime_cycle(
    *,
    state: RegimeState,
    current_price: Decimal,
    reference_price: Decimal,
    ema19: Decimal,
    ema50: Decimal,
    ema200: Decimal,
    trade_active: bool,
    config: RegimeConfig,
) -> RegimeResult:

    state.cycle += 1


    direction = (
        determine_direction_from_ema(
            ema19,
            ema50,
            ema200,
        )
    )


    state.last_direction = (
        direction
    )


    ema_separation = (
        percentage_distance(
            ema19,
            ema50,
        )
    )


    movement = (
        calculate_move_percent(
            current_price,
            reference_price,
        )
    )


    (
        raw_mode,
        classifier_reason,
    ) = classify_raw_regime(

        direction=direction,

        ema_separation_percent=
            ema_separation,

        short_term_move_percent=
            movement,

        config=config,

    )


    active_mode = (
        update_active_mode(

            state=state,

            raw_mode=raw_mode,

            reason=classifier_reason,

            trade_active=trade_active,

            config=config,

        )
    )


    valid_modes = (
        "SCALP",
        "STRUCTURE",
        "BREAKOUT",
    )


    if (
        config.exclusive_mode
        and
        active_mode not in valid_modes
    ):

        raise RuntimeError(
            "UNIT 4 EXCLUSIVE MODE FAILURE"
        )


    return RegimeResult(

        cycle=
            state.cycle,

        raw_mode=
            raw_mode,

        active_mode=
            active_mode,

        direction=
            direction,

        ema_separation_percent=
            ema_separation,

        short_term_move_percent=
            movement,

        pending_mode=
            state.pending_mode,

        pending_count=
            state.pending_count,

        mode_locked=
            state.mode_locked,

        reason=
            str(
                state.last_reason
            ),

        real_execution=False,

        demo_execution=False,

        write_transport=False,

    )


# ============================================================
# END PART 1 OF 2
# PART 2 CONTINUES WITH UNIT 4 LOCAL REGIME TESTS
# ============================================================
