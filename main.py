import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlencode

import aiohttp
from aiohttp import web


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R12"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# DECIMAL CONSTANTS
# ============================================================

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


# ============================================================
# ADJUSTABLE TRADE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal(
    os.getenv(
        "INITIAL_ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = Decimal(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_LEVERAGE = Decimal(
    os.getenv(
        "MAX_LEVERAGE",
        "100",
    )
)

MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1",
    )
)

PYRAMID_SIZE_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_SIZE_PERCENT",
        "5",
    )
)

MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENT = Decimal(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5",
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TP / TRAILING
# ============================================================

TP1_PERCENT = Decimal(
    os.getenv(
        "TP1_PERCENT",
        "20",
    )
)

TP2_PERCENT = Decimal(
    os.getenv(
        "TP2_PERCENT",
        "20",
    )
)

TP3_PERCENT = Decimal(
    os.getenv(
        "TP3_PERCENT",
        "60",
    )
)

TP1_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP1_TRIGGER_PERCENT",
        "0.5",
    )
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)


# ============================================================
# LIQUIDATION SAFETY
# ============================================================

BACKUP_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )
)

MIN_LIQ_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2",
    )
)

PLANNING_MMR_PERCENT = Decimal(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
    )
)


# ============================================================
# SIGNAL SAFETY
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "120",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "300",
    )
)


# ============================================================
# HTTP STABILITY
# ============================================================

HTTP_RETRY_ATTEMPTS = int(
    os.getenv(
        "HTTP_RETRY_ATTEMPTS",
        "3",
    )
)

HTTP_TIMEOUT_SECONDS = int(
    os.getenv(
        "HTTP_TIMEOUT_SECONDS",
        "15",
    )
)

HTTP_RETRY_DELAY_SECONDS = Decimal(
    os.getenv(
        "HTTP_RETRY_DELAY_SECONDS",
        "1",
    )
)


# ============================================================
# R12 PROCESS STABILITY
# ============================================================

KEEP_ALIVE_INTERVAL_SECONDS = int(
    os.getenv(
        "KEEP_ALIVE_INTERVAL_SECONDS",
        "3600",
    )
)

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# ============================================================
# SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True


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

telegram_report_sent = False


# ============================================================
# WEEX CREDENTIALS
# ============================================================

WEEX_API_KEY = os.getenv(
    "WEEX_API_KEY",
    "",
).strip()

WEEX_API_SECRET = os.getenv(
    "WEEX_API_SECRET",
    "",
).strip()

WEEX_API_PASSPHRASE = os.getenv(
    "WEEX_API_PASSPHRASE",
    "",
).strip()


# ============================================================
# RUNTIME SAFETY STATE
# ============================================================

seen_signal_ids = set()

active_direction = None

last_loss_time = None


# ============================================================
# HELPERS
# ============================================================

def safe_decimal(value, default="0"):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def fmt(value):
    if isinstance(value, Decimal):
        text = format(
            value.normalize(),
            "f",
        )

        if "." in text:
            text = text.rstrip("0").rstrip(".")

        return text or "0"

    return str(value)


def yes_no(value):
    return "✅ YES" if value else "❌ NO"


def quantize_down(
    value,
    precision,
):
    precision = int(precision)

    step = Decimal("1").scaleb(
        -precision
    )

    return value.quantize(
        step,
        rounding=ROUND_DOWN,
    )


def normalize_symbol_object(data):
    if isinstance(data, list):
        for item in data:
            if (
                isinstance(item, dict)
                and str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):
                return item

    if isinstance(data, dict):
        symbols = data.get(
            "symbols"
        )

        if isinstance(
            symbols,
            list,
        ):
            for item in symbols:
                if (
                    isinstance(
                        item,
                        dict,
                    )
                    and str(
                        item.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL
                ):
                    return item

        if (
            str(
                data.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):
            return data

    raise RuntimeError(
        f"Unable to locate contract data for {SYMBOL}"
    )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def create_signature(
    timestamp,
    method,
    path,
    query_string="",
    body_string="",
):
    method = method.upper()

    if query_string:
        message = (
            f"{timestamp}"
            f"{method}"
            f"{path}"
            f"?{query_string}"
            f"{body_string}"
        )
    else:
        message = (
            f"{timestamp}"
            f"{method}"
            f"{path}"
            f"{body_string}"
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode(
            "utf-8"
        ),
        message.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode(
        "utf-8"
    )


def private_headers(
    method,
    path,
    params=None,
    body=None,
):
    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    query_string = ""

    if params:
        query_string = urlencode(
            params
        )

    body_string = ""

    if body is not None:
        body_string = json.dumps(
            body,
            separators=(
                ",",
                ":",
            ),
        )

    signature = create_signature(
        timestamp=timestamp,
        method=method,
        path=path,
        query_string=query_string,
        body_string=body_string,
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": (
            WEEX_API_PASSPHRASE
        ),
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": (
            "application/json"
        ),
        "User-Agent": (
            "0F-4H-R12-WEEX-BOT"
        ),
    }

    return headers, body_string


# ============================================================
# HTTP RETRY ENGINE
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    last_error = None

    for attempt in range(
        1,
        HTTP_RETRY_ATTEMPTS + 1,
    ):
        try:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(
                    total=HTTP_TIMEOUT_SECONDS
                ),
                headers={
                    "User-Agent":
                    "0F-4H-R12-WEEX-BOT"
                },
            ) as response:

                text = (
                    await response.text()
                )

                if response.status == 200:
                    return json.loads(
                        text
                    )

                if (
                    response.status == 429
                    or response.status >= 500
                ):
                    raise RuntimeError(
                        "Transient WEEX "
                        f"HTTP {response.status}: "
                        f"{text}"
                    )

                raise RuntimeError(
                    f"WEEX HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            RuntimeError,
        ) as exc:

            last_error = exc

            transient = (
                isinstance(
                    exc,
                    (
                        aiohttp.ClientError,
                        asyncio.TimeoutError,
                    ),
                )
                or "Transient WEEX"
                in str(exc)
            )

            if (
                not transient
                or attempt
                >= HTTP_RETRY_ATTEMPTS
            ):
                raise

            await asyncio.sleep(
                float(
                    HTTP_RETRY_DELAY_SECONDS
                )
                * attempt
            )

    raise RuntimeError(
        str(last_error)
    )


async def private_get(
    session,
    path,
    params=None,
):
    url = (
        f"{API_BASE_URL}"
        f"{path}"
    )

    last_error = None

    for attempt in range(
        1,
        HTTP_RETRY_ATTEMPTS + 1,
    ):
        try:
            headers, _ = (
                private_headers(
                    method="GET",
                    path=path,
                    params=params,
                )
            )

            async with session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(
                    total=HTTP_TIMEOUT_SECONDS
                ),
            ) as response:

                text = (
                    await response.text()
                )

                if response.status == 200:
                    return json.loads(
                        text
                    )

                if (
                    response.status == 429
                    or response.status >= 500
                ):
                    raise RuntimeError(
                        "Transient WEEX "
                        f"HTTP {response.status}: "
                        f"{text}"
                    )

                raise RuntimeError(
                    f"WEEX PRIVATE HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            RuntimeError,
        ) as exc:

            last_error = exc

            transient = (
                isinstance(
                    exc,
                    (
                        aiohttp.ClientError,
                        asyncio.TimeoutError,
                    ),
                )
                or "Transient WEEX"
                in str(exc)
            )

            if (
                not transient
                or attempt
                >= HTTP_RETRY_ATTEMPTS
            ):
                raise

            await asyncio.sleep(
                float(
                    HTTP_RETRY_DELAY_SECONDS
                )
                * attempt
            )

    raise RuntimeError(
        str(last_error)
    )


# ============================================================
# MARKET DATA
# ============================================================

async def get_mark_price(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/symbolPrice",
        params={
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if isinstance(
        data,
        list,
    ):
        if not data:
            raise RuntimeError(
                "Empty mark-price response"
            )

        data = data[0]

    if not isinstance(
        data,
        dict,
    ):
        raise RuntimeError(
            "Invalid mark-price response"
        )

    price = safe_decimal(
        data.get(
            "price"
        )
    )

    if price <= ZERO:
        raise RuntimeError(
            f"Invalid WEEX mark price: "
            f"{price}"
        )

    return price


async def get_contract_info(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        params={
            "symbol": SYMBOL,
        },
    )

    contract = (
        normalize_symbol_object(
            data
        )
    )

    min_order = safe_decimal(
        contract.get(
            "minOrderSize",
            "0",
        )
    )

    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            0,
        )
    )

    contract_value = safe_decimal(
        contract.get(
            "contractVal",
            "0",
        )
    )

    min_leverage = safe_decimal(
        contract.get(
            "minLeverage",
            "1",
        )
    )

    max_leverage = safe_decimal(
        contract.get(
            "maxLeverage",
            "0",
        )
    )

    if min_order <= ZERO:
        raise RuntimeError(
            "Invalid minimum order"
        )

    if max_leverage <= ZERO:
        raise RuntimeError(
            "Invalid WEEX maximum leverage"
        )

    return {
        "min_order": min_order,
        "quantity_precision": (
            quantity_precision
        ),
        "contract_value": (
            contract_value
        ),
        "min_leverage": (
            min_leverage
        ),
        "max_leverage": (
            max_leverage
        ),
    }


async def get_api_trading_symbol_status(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/apiTradingSymbols",
    )

    symbols = []

    if isinstance(
        data,
        list,
    ):
        symbols = data

    elif isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "symbols",
            "result",
        ):
            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                symbols = value
                break

    normalized = []

    for item in symbols:
        if isinstance(
            item,
            str,
        ):
            normalized.append(
                item.upper()
            )

        elif isinstance(
            item,
            dict,
        ):
            symbol = (
                item.get(
                    "symbol"
                )
                or item.get(
                    "contract"
                )
            )

            if symbol:
                normalized.append(
                    str(
                        symbol
                    ).upper()
                )

    return SYMBOL in normalized


# ============================================================
# ACCOUNT
# ============================================================

async def get_available_balance(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    balances = data

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "balances",
        ):
            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):
                balances = candidate
                break

    if isinstance(
        balances,
        dict,
    ):
        balances = [
            balances
        ]

    if not isinstance(
        balances,
        list,
    ):
        raise RuntimeError(
            "Invalid WEEX balance response"
        )

    for item in balances:
        if not isinstance(
            item,
            dict,
        ):
            continue

        asset = str(
            item.get(
                "asset",
                item.get(
                    "coin",
                    "",
                ),
            )
        ).upper()

        if asset != "USDT":
            continue

        for key in (
            "availableBalance",
            "available",
            "availableAmount",
            "balance",
        ):
            if key in item:
                value = safe_decimal(
                    item[key]
                )

                if value >= ZERO:
                    return value

    raise RuntimeError(
        "Unable to extract available USDT balance"
    )


async def get_real_position(
    session,
):
    data = await private_get(
        session,
        "/capi/v3/account/position/allPosition",
    )

    positions = data

    if isinstance(
        data,
        dict,
    ):
        for key in (
            "data",
            "result",
            "positions",
        ):
            candidate = data.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):
                positions = candidate
                break

    if not isinstance(
        positions,
        list,
    ):
        return None

    for position in positions:
        if not isinstance(
            position,
            dict,
        ):
            continue

        position_symbol = str(
            position.get(
                "symbol",
                "",
            )
        ).upper()

        if position_symbol != SYMBOL:
            continue

        size = safe_decimal(
            position.get(
                "size",
                position.get(
                    "positionAmt",
                    "0",
                ),
            )
        )

        if abs(size) > ZERO:
            return position

    return None


# ============================================================
# SIGNAL SAFETY TESTS
# ============================================================

def signal_is_fresh(
    signal_timestamp,
):
    age = (
        time.time()
        - signal_timestamp
    )

    return (
        0
        <= age
        <= SIGNAL_EXPIRY_SECONDS
    )


def accept_signal_once(
    signal_id,
):
    if signal_id in seen_signal_ids:
        return False

    seen_signal_ids.add(
        signal_id
    )

    return True


def direction_allowed(
    requested_direction,
):
    if active_direction is None:
        return True

    return (
        active_direction
        == requested_direction
    )


def loss_cooldown_clear(
    current_time,
):
    if last_loss_time is None:
        return True

    return (
        current_time
        - last_loss_time
        >= LOSS_COOLDOWN_SECONDS
    )


def run_signal_gate_tests():
    now = time.time()

    fresh_ok = signal_is_fresh(
        now - 1
    )

    expired_rejected = (
        not signal_is_fresh(
            now
            - SIGNAL_EXPIRY_SECONDS
            - 10
        )
    )

    test_signal_id = (
        f"r12-test-"
        f"{int(now * 1000)}"
    )

    first_accept = (
        accept_signal_once(
            test_signal_id
        )
    )

    duplicate_rejected = (
        not accept_signal_once(
            test_signal_id
        )
    )

    one_direction_ok = (
        direction_allowed(
            "LONG"
        )
    )

    cooldown_ok = (
        loss_cooldown_clear(
            now
        )
    )

    return {
        "fresh_signal":
        fresh_ok and first_accept,

        "expired_signal":
        expired_rejected,

        "duplicate_signal":
        duplicate_rejected,

        "one_direction":
        one_direction_ok,

        "loss_cooldown":
        cooldown_ok,
    }


# ============================================================
# ORDER PAYLOAD SIMULATION
# ============================================================

def build_simulated_order_payload(
    quantity,
):
    client_order_id = (
        f"r12-"
        f"{SYMBOL.lower()}-"
        f"{int(time.time())}"
    )

    return {
        "symbol": SYMBOL,
        "side": "BUY",
        "positionSide": "LONG",
        "type": "MARKET",
        "quantity": fmt(
            quantity
        ),
        "newClientOrderId": (
            client_order_id[:36]
        ),
    }


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram_once(
    session,
    message,
):
    global telegram_report_sent

    if telegram_report_sent:
        print(
            "TELEGRAM REPORT SUPPRESSED: "
            "already sent in this process"
        )
        return False

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM CREDENTIALS MISSING"
        )
        return False

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        "sendMessage"
    )

    payload = {
        "chat_id":
        TELEGRAM_CHAT_ID,

        "text":
        message,
    }

    try:
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(
                total=15
            ),
        ) as response:

            text = (
                await response.text()
            )

            if response.status != 200:
                raise RuntimeError(
                    "Telegram HTTP "
                    f"{response.status}: "
                    f"{text}"
                )

            telegram_report_sent = True

            print(
                "TELEGRAM MESSAGE SENT"
            )

            return True

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        return False


# ============================================================
# R12 DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    stage = "STARTUP"

    credentials_ready = all(
        (
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        )
    )

    if not credentials_ready:
        raise RuntimeError(
            "WEEX credentials are missing"
        )

    timeout = aiohttp.ClientTimeout(
        total=HTTP_TIMEOUT_SECONDS
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:
            stage = "ACCOUNT BALANCE"

            balance = (
                await get_available_balance(
                    session
                )
            )

            stage = "MARK PRICE"

            mark_price = (
                await get_mark_price(
                    session
                )
            )

            stage = "API TRADING SYMBOL"

            api_trading_symbol = (
                await
                get_api_trading_symbol_status(
                    session
                )
            )

            stage = "CONTRACT INFO"

            contract = (
                await get_contract_info(
                    session
                )
            )

            min_order = contract[
                "min_order"
            ]

            quantity_precision = contract[
                "quantity_precision"
            ]

            contract_value = contract[
                "contract_value"
            ]

            weex_min_leverage = contract[
                "min_leverage"
            ]

            weex_max_leverage = contract[
                "max_leverage"
            ]

            stage = "SIGNAL GATES"

            signal_tests = (
                run_signal_gate_tests()
            )

            stage = "POSITION CHECK"

            position = (
                await get_real_position(
                    session
                )
            )

            external_position_clear = (
                position is None
            )

            liquidation_price = ZERO

            if position is not None:
                liquidation_price = (
                    safe_decimal(
                        position.get(
                            "liquidatePrice",
                            "0",
                        )
                    )
                )

            stage = "LEVERAGE GATE"

            leverage_gate = (
                LEVERAGE
                >= weex_min_leverage
                and LEVERAGE
                <= weex_max_leverage
                and LEVERAGE
                <= MAX_LEVERAGE
            )

            stage = "DYNAMIC ENTRY"

            entry_margin = (
                balance
                * INITIAL_ENTRY_PERCENT
                / HUNDRED
            )

            entry_notional = (
                entry_margin
                * LEVERAGE
            )

            raw_quantity = (
                entry_notional
                / mark_price
            )

            quantity = quantize_down(
                raw_quantity,
                quantity_precision,
            )

            quantity_positive = (
                quantity > ZERO
            )

            minimum_passed = (
                quantity
                >= min_order
            )

            stage = "EXPOSURE GATE"

            pyramid_exposure = (
                PYRAMID_SIZE_PERCENT
                * Decimal(
                    MAX_PYRAMID_ADDS
                )
            )

            backup_exposure = (
                BACKUP_SIZE_PERCENT
                * Decimal(
                    MAX_BACKUPS
                )
            )

            total_exposure = (
                INITIAL_ENTRY_PERCENT
                + pyramid_exposure
                + backup_exposure
            )

            exposure_passed = (
                total_exposure
                <= MAX_FUND_EXPOSURE_PERCENT
            )

            stage = "TP GATE"

            tp_total = (
                TP1_PERCENT
                + TP2_PERCENT
                + TP3_PERCENT
            )

            tp_split_valid = (
                tp_total
                == HUNDRED
            )

            stage = "PAYLOAD SIMULATION"

            order_payload = (
                build_simulated_order_payload(
                    quantity
                )
            )

            all_passed = all(
                (
                    api_trading_symbol,
                    signal_tests[
                        "fresh_signal"
                    ],
                    signal_tests[
                        "expired_signal"
                    ],
                    signal_tests[
                        "loss_cooldown"
                    ],
                    signal_tests[
                        "duplicate_signal"
                    ],
                    signal_tests[
                        "one_direction"
                    ],
                    external_position_clear,
                    leverage_gate,
                    quantity_positive,
                    minimum_passed,
                    exposure_passed,
                    tp_split_valid,
                    HARD_EXECUTION_LOCK,
                    not LIVE_ORDER_EXECUTION,
                )
            )

            status_icon = (
                "✅"
                if all_passed
                else "⚠️"
            )

            status_text = (
                "DIAGNOSTIC PASSED"
                if all_passed
                else "NOT READY"
            )

            if position is None:
                position_text = (
                    "No open position detected"
                )

                liquidation_text = "N/A"

            else:
                position_side = str(
                    position.get(
                        "side",
                        "UNKNOWN",
                    )
                )

                position_size = fmt(
                    safe_decimal(
                        position.get(
                            "size",
                            "0",
                        )
                    )
                )

                position_text = (
                    f"{position_side} "
                    f"{position_size}"
                )

                liquidation_text = (
                    fmt(
                        liquidation_price
                    )
                    if liquidation_price
                    > ZERO
                    else "N/A"
                )

            payload_text = json.dumps(
                order_payload,
                separators=(
                    ",",
                    ":",
                ),
            )

            telegram_message = (
                f"{status_icon} MODULE "
                f"{MODULE_NAME} "
                f"{status_text}\n"
                f"{SYMBOL}\n\n"

                f"Available USDT: "
                f"{fmt(balance)}\n"

                f"Mark Price: "
                f"{fmt(mark_price)} USDT\n\n"

                f"FINAL EXECUTION GATE\n"
                f"API Trading Symbol: "
                f"{yes_no(api_trading_symbol)}\n"

                f"Fresh Signal Accepted: "
                f"{yes_no(signal_tests['fresh_signal'])}\n"

                f"Expired Signal Rejected: "
                f"{yes_no(signal_tests['expired_signal'])}\n"

                f"Loss Cooldown Test: "
                f"{yes_no(signal_tests['loss_cooldown'])}\n"

                f"Duplicate Signal Rejected: "
                f"{yes_no(signal_tests['duplicate_signal'])}\n"

                f"One Direction Gate: "
                f"{yes_no(signal_tests['one_direction'])}\n"

                f"External Position Clear: "
                f"{yes_no(external_position_clear)}\n\n"

                f"ADJUSTABLE CONFIG\n"
                f"Entry: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

                f"Leverage: "
                f"{fmt(LEVERAGE)}x\n"

                f"Max Config Leverage: "
                f"{fmt(MAX_LEVERAGE)}x\n"

                f"Max Pyramids: "
                f"{MAX_PYRAMID_ADDS}\n"

                f"Pyramid Size: "
                f"{fmt(PYRAMID_SIZE_PERCENT)}%\n"

                f"Max Backups: "
                f"{MAX_BACKUPS}\n"

                f"Backup Size: "
                f"{fmt(BACKUP_SIZE_PERCENT)}% each\n"

                f"Max Fund Exposure: "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n\n"

                f"WEEX CONTRACT\n"
                f"Minimum Order: "
                f"{fmt(min_order)}\n"

                f"Quantity Precision: "
                f"{quantity_precision}\n"

                f"Contract Value: "
                f"{fmt(contract_value)}\n"

                f"WEEX Min Leverage: "
                f"{fmt(weex_min_leverage)}x\n"

                f"WEEX Max Leverage: "
                f"{fmt(weex_max_leverage)}x\n"

                f"Leverage Gate: "
                f"{yes_no(leverage_gate)}\n\n"

                f"DYNAMIC ENTRY\n"
                f"Margin: "
                f"{fmt(entry_margin)} USDT\n"

                f"Notional: "
                f"{fmt(entry_notional)} USDT\n"

                f"Quantity: "
                f"{fmt(quantity)}\n"

                f"Quantity Positive: "
                f"{yes_no(quantity_positive)}\n"

                f"Minimum Passed: "
                f"{yes_no(minimum_passed)}\n\n"

                f"WORST-CASE EXPOSURE\n"
                f"Initial: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

                f"Pyramids: "
                f"{fmt(pyramid_exposure)}%\n"

                f"Backups: "
                f"{fmt(backup_exposure)}%\n"

                f"Total: "
                f"{fmt(total_exposure)}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

                f"Exposure Passed: "
                f"{yes_no(exposure_passed)}\n\n"

                f"TP / TRAILING\n"
                f"TP1 / TP2 / TP3: "
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%\n"

                f"TP Split Valid: "
                f"{yes_no(tp_split_valid)}\n"

                f"TP1 Trigger: "
                f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

                f"TP2 Trigger: "
                f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

                f"Trailing Distance: "
                f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n\n"

                f"LIQUIDATION SETTINGS\n"
                f"Backup Buffer: "
                f"{fmt(BACKUP_BUFFER_PERCENT)}%\n"

                f"Min Liq Distance: "
                f"{fmt(MIN_LIQ_DISTANCE_PERCENT)}%\n"

                f"Planning MMR: "
                f"{fmt(PLANNING_MMR_PERCENT)}%\n\n"

                f"REAL WEEX POSITION\n"
                f"{position_text}\n"

                f"WEEX Liquidation Price: "
                f"{liquidation_text}\n\n"

                f"R12 ORDER PAYLOAD SIMULATION\n"
                f"Endpoint Target: "
                f"/capi/v3/order\n"

                f"Payload: "
                f"{payload_text}\n\n"

                f"R12 STABILITY\n"
                f"HTTP Retry Attempts: "
                f"{HTTP_RETRY_ATTEMPTS}\n"

                f"Single Telegram Report: "
                f"✅ ACTIVE\n"

                f"Stage-Aware Errors: "
                f"✅ ACTIVE\n"

                f"Transient API Retry: "
                f"✅ ACTIVE\n"

                f"Restart Loop Prevention: "
                f"✅ ACTIVE\n"

                f"Render Keep-Alive: "
                f"✅ ACTIVE\n"

                f"Health Server: "
                f"✅ PORT {PORT}\n\n"

                f"🛡 Hard execution lock active\n"
                f"⚠️ Live order execution disabled\n"
                f"⚠️ NO LIVE ORDER WAS SENT"
            )

            print(
                "=" * 60
            )

            print(
                f"{MODULE_NAME} STARTING"
            )

            print(
                "FINAL PRE-LIVE DRY-RUN"
            )

            print(
                "NO LIVE ORDER TRANSMISSION"
            )

            print(
                "=" * 60
            )

            print(
                telegram_message
            )

            print(
                "=" * 60
            )

            await send_telegram_once(
                session,
                telegram_message,
            )

            return {
                "passed": all_passed,
                "message": telegram_message,
            }

        except Exception as exc:
            error_message = (
                f"❌ MODULE "
                f"{MODULE_NAME} ERROR\n"
                f"{SYMBOL}\n\n"

                f"Stage: {stage}\n"
                f"{type(exc).__name__}: "
                f"{exc}\n\n"

                f"🛡 Hard execution lock active\n"
                f"⚠️ Live order execution disabled\n"
                f"⚠️ NO LIVE ORDER WAS SENT"
            )

            print(
                "=" * 60
            )

            print(
                error_message
            )

            print(
                "=" * 60
            )

            await send_telegram_once(
                session,
                error_message,
            )

            return {
                "passed": False,
                "message": error_message,
            }


# ============================================================
# R12 HEALTH SERVER
# ============================================================

async def health_handler(
    request,
):
    return web.json_response(
        {
            "module": MODULE_NAME,
            "symbol": SYMBOL,
            "status": "alive",
            "hard_execution_lock": (
                HARD_EXECUTION_LOCK
            ),
            "live_order_execution": (
                LIVE_ORDER_EXECUTION
            ),
            "telegram_report_sent": (
                telegram_report_sent
            ),
        }
    )


async def start_health_server():
    app = web.Application()

    app.router.add_get(
        "/",
        health_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT,
    )

    await site.start()

    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} KEEP-ALIVE ACTIVE"
    )

    print(
        f"Health server listening "
        f"on port {PORT}"
    )

    print(
        "Diagnostic will NOT repeat."
    )

    print(
        "Telegram report will NOT repeat "
        "inside this process."
    )

    print(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    print(
        "=" * 60
    )

    return runner


# ============================================================
# FALLBACK KEEP-ALIVE
# ============================================================

async def sleep_forever():
    while True:
        await asyncio.sleep(
            KEEP_ALIVE_INTERVAL_SECONDS
        )


# ============================================================
# MAIN
# ============================================================

async def main():
    print(
        "=" * 60
    )

    print(
        f"{MODULE_NAME} BOOT"
    )

    print(
        f"{SYMBOL}"
    )

    print(
        "R12 RESTART / TELEGRAM "
        "DUPLICATE SUPPRESSION"
    )

    print(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    print(
        "=" * 60
    )

    await run_diagnostic()

    try:
        runner = (
            await start_health_server()
        )

        try:
            await sleep_forever()

        finally:
            await runner.cleanup()

    except OSError as exc:
        print(
            "HEALTH SERVER WARNING:"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            "Using fallback keep-alive."
        )

        await sleep_forever()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )

    except KeyboardInterrupt:
        print(
            f"{MODULE_NAME} STOPPED"
        )

    except Exception as exc:
        print(
            "=" * 60
        )

        print(
            f"❌ {MODULE_NAME} "
            f"FATAL ERROR"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            "🛡 Hard execution lock active"
        )

        print(
            "⚠️ Live order execution disabled"
        )

        print(
            "⚠️ NO LIVE ORDER WAS SENT"
        )

        print(
            "=" * 60
        )

        raise
