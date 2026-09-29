#!/usr/bin/env python3

"""
FRESH WEEX TRADING BOT RECONSTRUCTION

UNIT 2
READ-ONLY WEEX TRANSPORT

BUILDS ON:
    UNIT 1 — FOUNDATION / CONFIGURATION / SAFETY

PURPOSE
-------
1. Preserve the tested Unit 1 foundation.
2. Add a clean WEEX GET-only transport.
3. Test public BTC market-price retrieval.
4. Test authenticated WEEX demo balance retrieval.
5. Test authenticated WEEX demo position retrieval.
6. Normalize exchange responses before later units consume them.

CRITICAL SAFETY PROPERTY
------------------------
There is NO POST transport function in this program.

ZERO WEEX POST.
ZERO DEMO ORDER.
ZERO REAL ORDER.
ZERO EXCHANGE MUTATION.
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

APP_VERSION = "0.2.0"

RECONSTRUCTION_UNIT = "UNIT_2_READ_ONLY_WEEX"


# ============================================================
# WEEX READ-ONLY CONFIGURATION
# ============================================================

API_BASE_URL = "https://api-contract.weex.com"

PUBLIC_TICKER_SYMBOL = "cmt_btcusdt"

DEMO_SYMBOL = os.getenv(
    "WEEX_DEMO_SYMBOL",
    "BTCSUSDT",
).strip().upper()

DEMO_ASSET = os.getenv(
    "WEEX_DEMO_ASSET",
    "SUSDT",
).strip().upper()


# Existing verified demo READ endpoints.

DEMO_BALANCE_ENDPOINT = (
    "/capi/v3/sim/balance"
)

DEMO_POSITIONS_ENDPOINT = (
    "/capi/v3/sim/position/allPosition"
)


# ============================================================
# FOUNDATION — DECIMAL
# ============================================================

def D(value: Any) -> Decimal:

    return Decimal(
        str(value)
    )


def quantize_down(
    value: Any,
    step: Any,
) -> Decimal:

    value = D(value)
    step = D(step)

    if step <= 0:

        raise ValueError(
            "Quantization step must be positive."
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
# FOUNDATION — TIME / LOGGING
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
# STRATEGY CONFIG
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


@dataclass(
    frozen=True
)
class EMAConfig:

    fast_period: int = 19

    medium_period: int = 50

    slow_period: int = 200

    confirmation_candles: int = 1

    minimum_fast_medium_separation_percent: Decimal = (
        Decimal("0.01")
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


# ============================================================
# EXECUTION FIREBREAK
# ============================================================

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

    if not (
        Decimal("0")
        < config.entry_margin_percent
        <= Decimal("100")
    ):

        raise ValueError(
            "Invalid entry margin percent."
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

    if not (
        Decimal("0")
        < config.maximum_fund_exposure_percent
        <= Decimal("100")
    ):

        raise ValueError(
            "Invalid maximum exposure."
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

    if not (
        0
        < config.fast_period
        < config.medium_period
        < config.slow_period
    ):

        raise ValueError(
            "EMA periods must satisfy "
            "0 < FAST < MEDIUM < SLOW."
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

    total = (

        config.tp1_allocation_percent
        + config.tp2_allocation_percent
        + config.tp3_allocation_percent

    )

    if total != Decimal("100"):

        raise ValueError(
            "TP allocations must total 100 percent."
        )

    if (
        config.tp3_trailing_distance_percent
        <= 0
    ):

        raise ValueError(
            "TP3 trailing distance must be positive."
        )


def validate_execution_firebreak(
    config: ExecutionSafetyConfig,
) -> None:

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
# CREDENTIAL PRESENCE
# ============================================================

def get_weex_credentials() -> tuple:

    api_key = os.getenv(
        "WEEX_API_KEY",
        "",
    ).strip()

    api_secret = os.getenv(
        "WEEX_API_SECRET",
        "",
    ).strip()

    passphrase = os.getenv(
        "WEEX_API_PASSPHRASE",
        "",
    ).strip()

    if not api_key:

        raise RuntimeError(
            "WEEX_API_KEY missing."
        )

    if not api_secret:

        raise RuntimeError(
            "WEEX_API_SECRET missing."
        )

    if not passphrase:

        raise RuntimeError(
            "WEEX_API_PASSPHRASE missing."
        )

    return (
        api_key,
        api_secret,
        passphrase,
    )


# ============================================================
# SIGNATURE
# ============================================================

def build_signature(
    *,
    timestamp: str,
    method: str,
    request_path: str,
    api_secret: str,
    body: str = "",
) -> str:

    if method.upper() != "GET":

        raise RuntimeError(
            "UNIT 2 SIGNER REFUSES NON-GET METHOD."
        )

    prehash = (

        str(timestamp)
        + "GET"
        + request_path
        + body

    )

    digest = hmac.new(

        api_secret.encode(
            "utf-8"
        ),

        prehash.encode(
            "utf-8"
        ),

        hashlib.sha256,

    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


# ============================================================
# READ-ONLY HTTP TRANSPORT
# ============================================================

class ReadOnlyWeexClient:

    """
    WEEX client intentionally exposing ONLY GET.

    There is no post(), put(), patch() or delete() method.
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
        authenticated: bool = False,
    ) -> Any:

        if not path.startswith("/"):

            raise ValueError(
                "WEEX path must begin with '/'."
            )

        params = params or {}

        query_string = urlencode(
            params,
            doseq=True,
        )

        request_target = path

        if query_string:

            request_target += (
                "?" + query_string
            )

        url = (
            self.base_url
            + request_target
        )

        headers = {}

        if authenticated:

            (
                api_key,
                api_secret,
                passphrase,
            ) = get_weex_credentials()

            timestamp = str(
                int(
                    time.time()
                    * 1000
                )
            )

            signature = build_signature(

                timestamp=timestamp,

                method="GET",

                request_path=request_target,

                api_secret=api_secret,

                body="",

            )

            headers = {

                "ACCESS-KEY":
                    api_key,

                "ACCESS-SIGN":
                    signature,

                "ACCESS-TIMESTAMP":
                    timestamp,

                "ACCESS-PASSPHRASE":
                    passphrase,

                "Content-Type":
                    "application/json",

            }

        timeout = aiohttp.ClientTimeout(
            total=self.timeout_seconds
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                headers=headers,
            ) as response:

                response_text = (
                    await response.text()
                )

                if response.status >= 400:

                    raise RuntimeError(

                        "WEEX GET FAILED "
                        f"status={response.status} "
                        f"path={path} "
                        f"response={response_text[:500]}"

                    )

                try:

                    return json.loads(
                        response_text
                    )

                except json.JSONDecodeError:

                    raise RuntimeError(

                        "WEEX returned non-JSON response "
                        f"for GET {path}: "
                        f"{response_text[:500]}"

                    )


# ============================================================
# GENERIC RESPONSE NORMALIZATION
# ============================================================

def extract_rows(
    value: Any,
) -> list:

    """
    Safely locate list-like rows inside common WEEX response
    wrappers.

    This keeps exchange response-shape handling here instead
    of spreading it through future strategy code.
    """

    if isinstance(
        value,
        list,
    ):

        return value


    if not isinstance(
        value,
        dict,
    ):

        return []


    candidate_keys = (

        "data",
        "list",
        "rows",
        "positions",
        "orders",
        "result",

    )


    for key in candidate_keys:

        candidate = value.get(
            key
        )

        if isinstance(
            candidate,
            list,
        ):

            return candidate


        if isinstance(
            candidate,
            dict,
        ):

            nested = extract_rows(
                candidate
            )

            if nested:

                return nested


    return []


# ============================================================
# DECIMAL EXTRACTION
# ============================================================

def first_decimal(
    mapping: dict,
    keys: tuple,
) -> Decimal | None:

    for key in keys:

        if key not in mapping:

            continue

        raw = mapping.get(
            key
        )

        if raw in (
            None,
            "",
        ):

            continue

        try:

            return D(
                raw
            )

        except Exception:

            continue

    return None


# ============================================================
# PUBLIC TICKER NORMALIZATION
# ============================================================

def find_price_in_payload(
    payload: Any,
) -> Decimal | None:

    """
    Search a ticker response conservatively for a usable
    positive market-price field.
    """

    price_keys = (

        "markPrice",
        "mark_price",
        "last",
        "lastPrice",
        "last_price",
        "close",
        "price",

    )

    if isinstance(
        payload,
        dict,
    ):

        price = first_decimal(
            payload,
            price_keys,
        )

        if (
            price is not None
            and price > 0
        ):

            return price


        for value in payload.values():

            if isinstance(
                value,
                (dict, list),
            ):

                found = find_price_in_payload(
                    value
                )

                if found is not None:

                    return found


    elif isinstance(
        payload,
        list,
    ):

        for item in payload:

            found = find_price_in_payload(
                item
            )

            if found is not None:

                return found


    return None


# ============================================================
# PUBLIC MARKET PRICE
# ============================================================

async def load_public_btc_price(
    client: ReadOnlyWeexClient,
) -> dict:

    """
    Try the public ticker endpoint used by the reconstructed
    system.

    If WEEX changes a public response shape, the raw response
    is still isolated inside this function.
    """

    candidate_requests = (

        (
            "/capi/v2/market/ticker",
            {
                "symbol":
                    PUBLIC_TICKER_SYMBOL
            },
        ),

        (
            "/capi/v2/market/tickers",
            {
                "symbol":
                    PUBLIC_TICKER_SYMBOL
            },
        ),

    )


    errors = []


    for (
        path,
        params,
    ) in candidate_requests:

        try:

            payload = await client.get(

                path,

                params=params,

                authenticated=False,

            )


            price = find_price_in_payload(
                payload
            )


            if (
                price is not None
                and price > 0
            ):

                return {

                    "success": True,

                    "path": path,

                    "symbol":
                        PUBLIC_TICKER_SYMBOL,

                    "price":
                        price,

                    "raw":
                        payload,

                }


            errors.append(

                f"{path}: "
                "no positive price field found"

            )


        except Exception as exc:

            errors.append(

                f"{path}: {exc}"

            )


    return {

        "success": False,

        "symbol":
            PUBLIC_TICKER_SYMBOL,

        "price":
            None,

        "errors":
            errors,

    }


# ============================================================
# DEMO BALANCE NORMALIZATION
# ============================================================

def normalize_demo_balance(
    payload: Any,
) -> dict:

    """
    Normalize the demo balance response.

    We retain the raw response for diagnostics while exposing
    only clean fields to later reconstruction units.
    """

    candidate_dicts = []


    if isinstance(
        payload,
        dict,
    ):

        candidate_dicts.append(
            payload
        )


        data = payload.get(
            "data"
        )

        if isinstance(
            data,
            dict,
        ):

            candidate_dicts.append(
                data
            )


    rows = extract_rows(
        payload
    )


    for row in rows:

        if isinstance(
            row,
            dict,
        ):

            candidate_dicts.append(
                row
            )


    selected = None


    for candidate in candidate_dicts:

        asset = str(

            candidate.get(
                "asset"
            )

            or candidate.get(
                "currency"
            )

            or candidate.get(
                "coin"
            )

            or candidate.get(
                "marginCoin"
            )

            or ""

        ).strip().upper()


        if asset == DEMO_ASSET:

            selected = candidate

            break


    if selected is None:

        for candidate in candidate_dicts:

            balance = first_decimal(

                candidate,

                (
                    "available",
                    "availableBalance",
                    "available_balance",
                    "balance",
                    "equity",
                    "walletBalance",
                ),

            )

            if balance is not None:

                selected = candidate

                break


    if selected is None:

        return {

            "success": False,

            "asset":
                DEMO_ASSET,

            "available_balance":
                None,

            "total_balance":
                None,

            "reason":
                "NO_BALANCE_RECORD_FOUND",

            "raw":
                payload,

        }


    available = first_decimal(

        selected,

        (
            "available",
            "availableBalance",
            "available_balance",
            "free",
        ),

    )


    total = first_decimal(

        selected,

        (
            "balance",
            "equity",
            "walletBalance",
            "total",
            "totalBalance",
        ),

    )


    if (
        available is None
        and total is not None
    ):

        available = total


    return {

        "success":
            available is not None,

        "asset":
            DEMO_ASSET,

        "available_balance":
            available,

        "total_balance":
            total,

        "record":
            selected,

        "raw":
            payload,

    }


# ============================================================
# DEMO POSITION NORMALIZATION
# ============================================================

def normalize_position_direction(
    row: dict,
) -> str:

    for key in (

        "positionSide",
        "holdSide",
        "side",

    ):

        value = str(
            row.get(
                key
            )
            or ""
        ).strip().upper()


        if value in (
            "LONG",
            "BUY",
        ):

            return "LONG"


        if value in (
            "SHORT",
            "SELL",
        ):

            return "SHORT"


    return "UNKNOWN"


def normalize_position_size(
    row: dict,
) -> Decimal:

    size = first_decimal(

        row,

        (
            "size",
            "positionSize",
            "positionAmt",
            "quantity",
            "qty",
            "total",
        ),

    )

    if size is None:

        return Decimal("0")


    return abs(
        size
    )


def normalize_demo_positions(
    payload: Any,
) -> dict:

    rows = extract_rows(
        payload
    )

    normalized = []


    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue


        symbol = str(

            row.get(
                "symbol"
            )

            or row.get(
                "contractCode"
            )

            or ""

        ).strip().upper()


        size = normalize_position_size(
            row
        )


        direction = (
            normalize_position_direction(
                row
            )
        )


        entry_price = first_decimal(

            row,

            (
                "entryPrice",
                "avgPrice",
                "averageOpenPrice",
                "openPrice",
            ),

        )


        liquidation_price = first_decimal(

            row,

            (
                "liquidationPrice",
                "liquidation_price",
                "liqPrice",
                "liquidatePrice",
            ),

        )


        mark_price = first_decimal(

            row,

            (
                "markPrice",
                "mark_price",
            ),

        )


        normalized.append(

            {

                "symbol":
                    symbol,

                "direction":
                    direction,

                "size":
                    size,

                "entry_price":
                    entry_price,

                "liquidation_price":
                    liquidation_price,

                "mark_price":
                    mark_price,

                "active":
                    size > 0,

                "raw":
                    row,

            }

        )


    active = [

        position

        for position in normalized

        if position[
            "active"
        ]

    ]


    return {

        "success": True,

        "positions":
            normalized,

        "active_positions":
            active,

        "position_count":
            len(normalized),

        "active_position_count":
            len(active),

        "raw":
            payload,

    }


# ============================================================
# AUTHENTICATED READ FUNCTIONS
# ============================================================

async def load_demo_balance(
    client: ReadOnlyWeexClient,
) -> dict:

    payload = await client.get(

        DEMO_BALANCE_ENDPOINT,

        authenticated=True,

    )

    return normalize_demo_balance(
        payload
    )


async def load_demo_positions(
    client: ReadOnlyWeexClient,
) -> dict:

    payload = await client.get(

        DEMO_POSITIONS_ENDPOINT,

        authenticated=True,

    )

    return normalize_demo_positions(
        payload
    )


# ============================================================
# UNIT 1 FOUNDATION SELF-CHECK
# ============================================================

def run_foundation_check(
    config: AppConfig,
) -> None:

    validate_config(
        config
    )

    log(
        "PASS: UNIT 1 FOUNDATION CONFIG"
    )


    unsafe = ExecutionSafetyConfig(
        real_order_execution=True
    )


    rejected = False


    try:

        validate_execution_firebreak(
            unsafe
        )

    except RuntimeError:

        rejected = True


    if not rejected:

        raise RuntimeError(
            "Foundation firebreak test failed."
        )


    log(
        "PASS: UNIT 1 FIREBREAK"
    )


# ============================================================
# UNIT 2 STRUCTURAL SAFETY TEST
# ============================================================

def test_read_only_client_structure() -> None:

    forbidden_methods = (

        "post",
        "put",
        "patch",
        "delete",

    )


    for method in forbidden_methods:

        if hasattr(
            ReadOnlyWeexClient,
            method,
        ):

            raise RuntimeError(

                "READ-ONLY CLIENT EXPOSES "
                f"FORBIDDEN METHOD: {method}"

            )


    log(
        "PASS: READ-ONLY CLIENT HAS NO MUTATION METHODS"
    )


# ============================================================
# SIGNER SAFETY TEST
# ============================================================

def test_signer_rejects_post() -> None:

    rejected = False


    try:

        build_signature(

            timestamp="123456789",

            method="POST",

            request_path="/test",

            api_secret="unit-test-secret",

        )


    except RuntimeError:

        rejected = True


    if not rejected:

        raise RuntimeError(
            "Signer failed to reject POST."
        )


    log(
        "PASS: SIGNER REJECTS NON-GET METHOD"
    )


# ============================================================
# LOCAL NORMALIZER TESTS
# ============================================================

def test_normalizers() -> None:

    # --------------------------------------------------------
    # Balance normalizer
    # --------------------------------------------------------

    fake_balance = {

        "data": [

            {

                "asset":
                    DEMO_ASSET,

                "available":
                    "7.18945017",

                "balance":
                    "7.50000000",

            }

        ]

    }


    normalized_balance = (
        normalize_demo_balance(
            fake_balance
        )
    )


    if not normalized_balance[
        "success"
    ]:

        raise RuntimeError(
            "Balance normalizer test failed."
        )


    if normalized_balance[
        "available_balance"
    ] != Decimal("7.18945017"):

        raise RuntimeError(
            "Balance Decimal normalization failed."
        )


    log(
        "PASS: BALANCE NORMALIZER"
    )


    # --------------------------------------------------------
    # Position normalizer
    # --------------------------------------------------------

    fake_positions = {

        "data": [

            {

                "symbol":
                    DEMO_SYMBOL,

                "positionSide":
                    "SHORT",

                "size":
                    "0.0004",

                "entryPrice":
                    "83931.4",

                "liquidationPrice":
                    "80157.3",

            },

            {

                "symbol":
                    DEMO_SYMBOL,

                "positionSide":
                    "LONG",

                "size":
                    "0",

            },

        ]

    }


    normalized_positions = (
        normalize_demo_positions(
            fake_positions
        )
    )


    if (
        normalized_positions[
            "active_position_count"
        ]
        != 1
    ):

        raise RuntimeError(
            "Position active-count normalization failed."
        )


    first_active = (
        normalized_positions[
            "active_positions"
        ][0]
    )


    if (
        first_active[
            "direction"
        ]
        != "SHORT"
    ):

        raise RuntimeError(
            "Position direction normalization failed."
        )


    if (
        first_active[
            "size"
        ]
        != Decimal("0.0004")
    ):

        raise RuntimeError(
            "Position size normalization failed."
        )


    log(
        "PASS: POSITION NORMALIZER"
    )


# ============================================================
# LIVE READ-ONLY UNIT 2 TEST
# ============================================================

async def run_unit_2_test() -> bool:

    separator()

    log(
        "RECONSTRUCTION UNIT 2 TEST START"
    )

    separator()


    config = build_config()


    # --------------------------------------------------------
    # UNIT 1 MUST STILL PASS
    # --------------------------------------------------------

    run_foundation_check(
        config
    )


    # --------------------------------------------------------
    # UNIT 2 STRUCTURAL SAFETY
    # --------------------------------------------------------

    test_read_only_client_structure()

    test_signer_rejects_post()

    test_normalizers()


    # --------------------------------------------------------
    # VERIFY CREDENTIALS EXIST
    # --------------------------------------------------------

    get_weex_credentials()


    log(
        "PASS: WEEX CREDENTIALS PRESENT"
    )


    # --------------------------------------------------------
    # CREATE READ-ONLY CLIENT
    # --------------------------------------------------------

    client = ReadOnlyWeexClient()


    # --------------------------------------------------------
    # TEST PUBLIC BTC PRICE
    # --------------------------------------------------------

    separator()

    log(
        "UNIT 2 PUBLIC MARKET READ START"
    )


    market = await load_public_btc_price(
        client
    )


    if not market.get(
        "success"
    ):

        raise RuntimeError(

            "PUBLIC MARKET READ FAILED: "
            + repr(
                market.get(
                    "errors"
                )
            )

        )


    market_price = market[
        "price"
    ]


    if market_price <= 0:

        raise RuntimeError(
            "Public market price is non-positive."
        )


    log(
        "PASS: PUBLIC BTC MARKET READ"
    )

    log(
        "PUBLIC BTC PRICE = "
        + decimal_to_string(
            market_price
        )
    )

    log(
        "PUBLIC MARKET SOURCE = "
        + str(
            market.get(
                "path"
            )
        )
    )


    # --------------------------------------------------------
    # TEST DEMO BALANCE READ
    # --------------------------------------------------------

    separator()

    log(
        "UNIT 2 AUTHENTICATED DEMO BALANCE READ START"
    )


    balance = await load_demo_balance(
        client
    )


    if not balance.get(
        "success"
    ):

        raise RuntimeError(

            "DEMO BALANCE NORMALIZATION FAILED: "
            + str(
                balance.get(
                    "reason"
                )
            )

        )


    available_balance = (
        balance[
            "available_balance"
        ]
    )


    if available_balance < 0:

        raise RuntimeError(
            "Demo available balance is negative."
        )


    log(
        "PASS: AUTHENTICATED DEMO BALANCE READ"
    )

    log(
        "DEMO ASSET = "
        + DEMO_ASSET
    )

    log(
        "DEMO AVAILABLE BALANCE = "
        + decimal_to_string(
            available_balance
        )
    )


    # --------------------------------------------------------
    # TEST DEMO POSITION READ
    # --------------------------------------------------------

    separator()

    log(
        "UNIT 2 AUTHENTICATED DEMO POSITION READ START"
    )


    positions = await load_demo_positions(
        client
    )


    if not positions.get(
        "success"
    ):

        raise RuntimeError(
            "Demo position normalization failed."
        )


    log(
        "PASS: AUTHENTICATED DEMO POSITION READ"
    )

    log(
        "DEMO POSITION ROWS = "
        + str(
            positions[
                "position_count"
            ]
        )
    )

    log(
        "DEMO ACTIVE POSITIONS = "
        + str(
            positions[
                "active_position_count"
            ]
        )
    )


    for index, position in enumerate(

        positions[
            "active_positions"
        ],

        start=1,

    ):

        log(
            "ACTIVE POSITION "
            + str(index)
            + " SYMBOL = "
            + str(
                position[
                    "symbol"
                ]
            )
        )

        log(
            "ACTIVE POSITION "
            + str(index)
            + " DIRECTION = "
            + str(
                position[
                    "direction"
                ]
            )
        )

        log(
            "ACTIVE POSITION "
            + str(index)
            + " SIZE = "
            + decimal_to_string(
                position[
                    "size"
                ]
            )
        )


        if (
            position[
                "entry_price"
            ]
            is not None
        ):

            log(
                "ACTIVE POSITION "
                + str(index)
                + " ENTRY PRICE = "
                + decimal_to_string(
                    position[
                        "entry_price"
                    ]
                )
            )


        if (
            position[
                "liquidation_price"
            ]
            is not None
        ):

            log(
                "ACTIVE POSITION "
                + str(index)
                + " LIQUIDATION PRICE = "
                + decimal_to_string(
                    position[
                        "liquidation_price"
                    ]
                )
            )


    # --------------------------------------------------------
    # FINAL FIREBREAK REVALIDATION
    # --------------------------------------------------------

    separator()


    validate_execution_firebreak(
        config.execution
    )


    log(
        "PASS: FINAL EXECUTION FIREBREAK"
    )


    # --------------------------------------------------------
    # FINAL UNIT RESULT
    # --------------------------------------------------------

    separator()

    log(
        "ZERO WEEX POST = TRUE"
    )

    log(
        "ZERO DEMO ORDER = TRUE"
    )

    log(
        "ZERO REAL ORDER = TRUE"
    )

    log(
        "ZERO LEVERAGE MUTATION = TRUE"
    )

    log(
        "ZERO MARGIN MODE MUTATION = TRUE"
    )

    log(
        "ZERO POSITION MUTATION = TRUE"
    )

    separator()

    log(
        "RECONSTRUCTION UNIT 2 RESULT = PASS"
    )

    separator()


    return True


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    log(
        f"{APP_NAME} {APP_VERSION}"
    )

    log(
        f"STARTING {RECONSTRUCTION_UNIT}"
    )


    try:

        passed = await run_unit_2_test()


    except Exception as exc:

        separator()

        log(
            "RECONSTRUCTION UNIT 2 RESULT = FAIL"
        )

        log(
            "ERROR = "
            + repr(
                exc
            )
        )

        separator()

        raise


    if not passed:

        raise RuntimeError(
            "Unit 2 did not pass."
        )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
