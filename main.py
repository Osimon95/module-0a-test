import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, ROUND_DOWN, InvalidOperation
from urllib.parse import urlencode

import aiohttp
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R3"

SYMBOL = "BTCUSDT"

API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# TRADE CONFIGURATION
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
        "5",
    )
)

MAX_LEVERAGE = Decimal(
    os.getenv(
        "MAX_LEVERAGE",
        "10",
    )
)

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# TEST MARGIN LEVELS
# ============================================================

TEST_MARGIN_1 = Decimal("1")
TEST_MARGIN_5 = Decimal("5")


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
# GENERAL SETTINGS
# ============================================================

REQUEST_TIMEOUT_SECONDS = 15

KEEP_ALIVE_SECONDS = 3600


# ============================================================
# PRINT HELPERS
# ============================================================

def separator():
    print("=" * 60, flush=True)


def log(message=""):
    print(message, flush=True)


# ============================================================
# DECIMAL HELPERS
# ============================================================

def D(value, default="0"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def decimal_text(value):
    value = D(value)

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_to_precision(
    value,
    precision,
):
    value = D(value)

    precision = int(precision)

    quantum = Decimal("1").scaleb(
        -precision
    )

    return value.quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN:
        log("TELEGRAM BOT TOKEN: MISSING")
        return

    if not TELEGRAM_CHAT_ID:
        log("TELEGRAM CHAT ID: MISSING")
        return

    try:
        bot = Bot(
            token=TELEGRAM_BOT_TOKEN
        )

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        log("TELEGRAM MESSAGE SENT")

    except Exception as exc:
        log(
            f"TELEGRAM ERROR: "
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# WEEX AUTHENTICATION
# ============================================================

def credentials_ready():
    return all(
        [
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        ]
    )


def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    message = (
        str(timestamp)
        + method.upper()
        + request_path
        + query_string
        + body
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


def authenticated_headers(
    timestamp,
    signature,
):
    return {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": str(timestamp),
        "Content-Type": "application/json",
        "locale": "en-US",
    }


# ============================================================
# HTTP HELPERS
# ============================================================

async def public_get(
    session,
    request_path,
    params=None,
):
    params = params or {}

    query_string = ""

    if params:
        query_string = (
            "?"
            + urlencode(params)
        )

    url = (
        API_BASE_URL
        + request_path
        + query_string
    )

    async with session.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                f"INVALID WEEX JSON: {text}"
            )


async def private_get(
    session,
    request_path,
    params=None,
):
    if not credentials_ready():
        raise RuntimeError(
            "WEEX credentials are missing"
        )

    params = params or {}

    query_string = ""

    if params:
        query_string = (
            "?"
            + urlencode(params)
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        timestamp=timestamp,
        method="GET",
        request_path=request_path,
        query_string=query_string,
        body="",
    )

    headers = authenticated_headers(
        timestamp,
        signature,
    )

    url = (
        API_BASE_URL
        + request_path
        + query_string
    )

    async with session.get(
        url,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE HTTP "
                f"{response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                f"INVALID WEEX JSON: {text}"
            )


# ============================================================
# GET BTCUSDT MARK PRICE
# ============================================================

async def get_mark_price(session):
    data = await public_get(
        session,
        "/capi/v3/market/symbolPrice",
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Unexpected symbol price response: "
            f"{data}"
        )

    price = D(
        data.get("price")
    )

    if price <= 0:
        raise RuntimeError(
            f"Invalid BTC mark price: "
            f"{data}"
        )

    return price


# ============================================================
# GET CONTRACT INFORMATION
# ============================================================

async def get_contract_info(session):
    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Unexpected exchangeInfo response: "
            f"{data}"
        )

    symbols = data.get(
        "symbols",
        [],
    )

    for item in symbols:
        if (
            str(
                item.get("symbol", "")
            ).upper()
            == SYMBOL
        ):
            return item

    raise RuntimeError(
        f"{SYMBOL} not found in "
        f"WEEX exchangeInfo"
    )


# ============================================================
# CHECK API-TRADABLE SYMBOL
# ============================================================

async def check_api_trading_symbol(
    session,
):
    data = await public_get(
        session,
        "/capi/v3/market/apiTradingSymbols",
    )

    if not isinstance(data, list):
        return False

    symbols = [
        str(item).upper()
        for item in data
    ]

    return SYMBOL in symbols


# ============================================================
# GET ACCOUNT BALANCE
# ============================================================

async def get_usdt_balance(session):
    data = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    if not isinstance(data, list):
        raise RuntimeError(
            f"Unexpected balance response: "
            f"{data}"
        )

    for asset in data:
        if (
            str(
                asset.get("asset", "")
            ).upper()
            == "USDT"
        ):

            available = D(
                asset.get(
                    "availableBalance",
                    "0",
                )
            )

            total = D(
                asset.get(
                    "balance",
                    "0",
                )
            )

            return {
                "available": available,
                "total": total,
                "raw": asset,
            }

    raise RuntimeError(
        "USDT was not found in "
        "WEEX futures balance"
    )


# ============================================================
# POSITION CALCULATIONS
# ============================================================

def calculate_quantity_from_margin(
    margin_usdt,
    price,
    leverage,
    quantity_precision,
):
    margin_usdt = D(
        margin_usdt
    )

    price = D(
        price
    )

    leverage = D(
        leverage
    )

    if margin_usdt <= 0:
        return Decimal("0")

    if price <= 0:
        return Decimal("0")

    if leverage <= 0:
        return Decimal("0")

    notional = (
        margin_usdt
        * leverage
    )

    raw_quantity = (
        notional
        / price
    )

    return floor_to_precision(
        raw_quantity,
        quantity_precision,
    )


def minimum_margin_required(
    min_order_size,
    price,
    leverage,
):
    min_order_size = D(
        min_order_size
    )

    price = D(
        price
    )

    leverage = D(
        leverage
    )

    if leverage <= 0:
        return Decimal("0")

    minimum_notional = (
        min_order_size
        * price
    )

    minimum_margin = (
        minimum_notional
        / leverage
    )

    return minimum_margin


def test_margin_amount(
    margin,
    price,
    leverage,
    min_order_size,
    quantity_precision,
):
    quantity = calculate_quantity_from_margin(
        margin_usdt=margin,
        price=price,
        leverage=leverage,
        quantity_precision=quantity_precision,
    )

    meets_minimum = (
        quantity >= min_order_size
    )

    notional = (
        quantity
        * price
    )

    return {
        "margin": margin,
        "quantity": quantity,
        "notional": notional,
        "meets_minimum": meets_minimum,
    }


# ============================================================
# MAIN DIAGNOSTIC
# ============================================================

async def run_diagnostic():
    separator()

    log(
        f"MODULE {MODULE_NAME} STARTING"
    )

    log(
        f"{SYMBOL} MINIMUM ORDER "
        f"+ MARGIN DIAGNOSTIC"
    )

    separator()

    log(
        f"Initial Entry: "
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    log(
        f"Leverage: {LEVERAGE}x"
    )

    log(
        f"Max Leverage: "
        f"{MAX_LEVERAGE}x"
    )

    log(
        f"Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    log(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    log(
        "HARD EXECUTION LOCK: ACTIVE"
    )

    separator()

    if not credentials_ready():
        raise RuntimeError(
            "WEEX API credentials are missing"
        )

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT_SECONDS
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        log(
            "REQUESTING BTCUSDT MARK PRICE..."
        )

        mark_price = await get_mark_price(
            session
        )

        log(
            f"MARK PRICE: "
            f"{decimal_text(mark_price)} USDT"
        )

        # ----------------------------------------------------
        # CONTRACT
        # ----------------------------------------------------

        log(
            "REQUESTING BTCUSDT "
            "CONTRACT INFORMATION..."
        )

        contract = await get_contract_info(
            session
        )

        quantity_precision = int(
            contract.get(
                "quantityPrecision",
                6,
            )
        )

        min_order_size = D(
            contract.get(
                "minOrderSize",
                "0",
            )
        )

        contract_val = D(
            contract.get(
                "contractVal",
                "0",
            )
        )

        min_leverage = D(
            contract.get(
                "minLeverage",
                "1",
            )
        )

        exchange_max_leverage = D(
            contract.get(
                "maxLeverage",
                "0",
            )
        )

        margin_asset = str(
            contract.get(
                "marginAsset",
                "",
            )
        )

        log(
            f"MIN ORDER SIZE: "
            f"{decimal_text(min_order_size)} BTC"
        )

        log(
            f"QUANTITY PRECISION: "
            f"{quantity_precision}"
        )

        log(
            f"CONTRACT VALUE: "
            f"{decimal_text(contract_val)}"
        )

        log(
            f"MARGIN ASSET: "
            f"{margin_asset}"
        )

        log(
            f"EXCHANGE LEVERAGE RANGE: "
            f"{decimal_text(min_leverage)}x "
            f"- "
            f"{decimal_text(exchange_max_leverage)}x"
        )

        # ----------------------------------------------------
        # API TRADING SYMBOL
        # ----------------------------------------------------

        api_tradable = (
            await check_api_trading_symbol(
                session
            )
        )

        log(
            f"API TRADING SYMBOL: "
            f"{'YES' if api_tradable else 'NO'}"
        )

        # ----------------------------------------------------
        # BALANCE
        # ----------------------------------------------------

        log(
            "REQUESTING AUTHENTICATED "
            "USDT BALANCE..."
        )

        balance = await get_usdt_balance(
            session
        )

        available_usdt = balance[
            "available"
        ]

        total_usdt = balance[
            "total"
        ]

        log(
            f"TOTAL USDT: "
            f"{decimal_text(total_usdt)}"
        )

        log(
            f"AVAILABLE USDT: "
            f"{decimal_text(available_usdt)}"
        )

        # ----------------------------------------------------
        # TRUE MINIMUM MARGIN
        # ----------------------------------------------------

        min_notional = (
            min_order_size
            * mark_price
        )

        min_margin = (
            minimum_margin_required(
                min_order_size,
                mark_price,
                LEVERAGE,
            )
        )

        balance_can_fund_minimum = (
            available_usdt
            >= min_margin
        )

        log("")
        separator()

        log(
            "TRUE MINIMUM ORDER CALCULATION"
        )

        separator()

        log(
            f"Minimum BTC: "
            f"{decimal_text(min_order_size)}"
        )

        log(
            f"Minimum Notional: "
            f"{decimal_text(min_notional)} USDT"
        )

        log(
            f"At {LEVERAGE}x leverage"
        )

        log(
            f"Minimum Margin Required: "
            f"{decimal_text(min_margin)} USDT"
        )

        log(
            f"Available Balance: "
            f"{decimal_text(available_usdt)} USDT"
        )

        log(
            f"Balance Can Fund Minimum: "
            f"{'YES' if balance_can_fund_minimum else 'NO'}"
        )

        # ----------------------------------------------------
        # ORIGINAL 5% ENTRY
        # ----------------------------------------------------

        initial_margin = (
            available_usdt
            * INITIAL_ENTRY_PERCENT
            / Decimal("100")
        )

        initial_quantity = (
            calculate_quantity_from_margin(
                margin_usdt=initial_margin,
                price=mark_price,
                leverage=LEVERAGE,
                quantity_precision=quantity_precision,
            )
        )

        initial_notional = (
            initial_quantity
            * mark_price
        )

        initial_meets_minimum = (
            initial_quantity
            >= min_order_size
        )

        log("")
        separator()

        log(
            "CURRENT 5% ENTRY TEST"
        )

        separator()

        log(
            f"Entry Margin: "
            f"{decimal_text(initial_margin)} USDT"
        )

        log(
            f"Leveraged Notional: "
            f"{decimal_text(initial_margin * LEVERAGE)} USDT"
        )

        log(
            f"Calculated Quantity: "
            f"{decimal_text(initial_quantity)} BTC"
        )

        log(
            f"Actual Rounded Notional: "
            f"{decimal_text(initial_notional)} USDT"
        )

        log(
            f"Meets Minimum Order: "
            f"{'YES' if initial_meets_minimum else 'NO'}"
        )

        # ----------------------------------------------------
        # $1 TEST
        # ----------------------------------------------------

        one_dollar = test_margin_amount(
            margin=TEST_MARGIN_1,
            price=mark_price,
            leverage=LEVERAGE,
            min_order_size=min_order_size,
            quantity_precision=quantity_precision,
        )

        # ----------------------------------------------------
        # $5 TEST
        # ----------------------------------------------------

        five_dollar = test_margin_amount(
            margin=TEST_MARGIN_5,
            price=mark_price,
            leverage=LEVERAGE,
            min_order_size=min_order_size,
            quantity_precision=quantity_precision,
        )

        log("")
        separator()

        log(
            "$1 USDT MARGIN TEST"
        )

        separator()

        log(
            f"Margin: "
            f"{decimal_text(one_dollar['margin'])} USDT"
        )

        log(
            f"Notional at {LEVERAGE}x: "
            f"{decimal_text(TEST_MARGIN_1 * LEVERAGE)} USDT"
        )

        log(
            f"Quantity: "
            f"{decimal_text(one_dollar['quantity'])} BTC"
        )

        log(
            f"Meets Minimum: "
            f"{'YES' if one_dollar['meets_minimum'] else 'NO'}"
        )

        log("")
        separator()

        log(
            "$5 USDT MARGIN TEST"
        )

        separator()

        log(
            f"Margin: "
            f"{decimal_text(five_dollar['margin'])} USDT"
        )

        log(
            f"Notional at {LEVERAGE}x: "
            f"{decimal_text(TEST_MARGIN_5 * LEVERAGE)} USDT"
        )

        log(
            f"Quantity: "
            f"{decimal_text(five_dollar['quantity'])} BTC"
        )

        log(
            f"Meets Minimum: "
            f"{'YES' if five_dollar['meets_minimum'] else 'NO'}"
        )

        # ----------------------------------------------------
        # MAXIMUM AFFORDABLE QUANTITY
        # ----------------------------------------------------

        max_affordable_quantity = (
            calculate_quantity_from_margin(
                margin_usdt=available_usdt,
                price=mark_price,
                leverage=LEVERAGE,
                quantity_precision=quantity_precision,
            )
        )

        log("")
        separator()

        log(
            "AVAILABLE BALANCE CAPACITY"
        )

        separator()

        log(
            f"Available Margin: "
            f"{decimal_text(available_usdt)} USDT"
        )

        log(
            f"At {LEVERAGE}x leverage"
        )

        log(
            f"Maximum Theoretical Quantity: "
            f"{decimal_text(max_affordable_quantity)} BTC"
        )

        # ----------------------------------------------------
        # SAFE VERDICT
        # ----------------------------------------------------

        failed_checks = []

        if mark_price <= 0:
            failed_checks.append(
                "valid_mark_price"
            )

        if min_order_size <= 0:
            failed_checks.append(
                "valid_min_order_size"
            )

        if not api_tradable:
            failed_checks.append(
                "api_trading_symbol"
            )

        if available_usdt <= 0:
            failed_checks.append(
                "positive_balance"
            )

        if not balance_can_fund_minimum:
            failed_checks.append(
                "balance_sufficient_for_minimum"
            )

        separator()

        if failed_checks:

            status = (
                f"⚠️ MODULE {MODULE_NAME} "
                f"DIAGNOSTIC WARNING"
            )

        else:

            status = (
                f"✅ MODULE {MODULE_NAME} "
                f"DIAGNOSTIC PASSED"
            )

        log(status)

        separator()

        if failed_checks:
            log("FAILED CHECKS:")

            for check in failed_checks:
                log(
                    f"❌ {check}"
                )

        else:
            log(
                "✅ WEEX V3 MARK PRICE"
            )

            log(
                "✅ WEEX CONTRACT INFO"
            )

            log(
                "✅ API TRADING SYMBOL"
            )

            log(
                "✅ AUTHENTICATED BALANCE"
            )

            log(
                "✅ TRUE MINIMUM MARGIN CALCULATED"
            )

        log(
            "🛡 HARD EXECUTION LOCK ACTIVE"
        )

        log(
            "⚠️ NO LIVE ORDER WAS SENT"
        )

        # ----------------------------------------------------
        # TELEGRAM REPORT
        # ----------------------------------------------------

        telegram_message = (
            f"{status}\n"
            f"{SYMBOL}\n\n"

            f"Mark Price: "
            f"{decimal_text(mark_price)} USDT\n"

            f"Available USDT: "
            f"{decimal_text(available_usdt)}\n\n"

            f"WEEX Contract\n"
            f"Minimum Order: "
            f"{decimal_text(min_order_size)} BTC\n"

            f"Quantity Precision: "
            f"{quantity_precision}\n"

            f"Contract Value: "
            f"{decimal_text(contract_val)}\n\n"

            f"TRUE MINIMUM AT {LEVERAGE}x\n"
            f"Minimum Notional: "
            f"{decimal_text(min_notional)} USDT\n"

            f"Minimum Margin Required: "
            f"{decimal_text(min_margin)} USDT\n"

            f"Balance Sufficient: "
            f"{'✅ YES' if balance_can_fund_minimum else '❌ NO'}\n\n"

            f"CURRENT {INITIAL_ENTRY_PERCENT}% ENTRY\n"
            f"Margin: "
            f"{decimal_text(initial_margin)} USDT\n"

            f"Quantity: "
            f"{decimal_text(initial_quantity)} BTC\n"

            f"Minimum Passed: "
            f"{'✅ YES' if initial_meets_minimum else '❌ NO'}\n\n"

            f"$1 MARGIN TEST\n"
            f"Quantity: "
            f"{decimal_text(one_dollar['quantity'])} BTC\n"

            f"Minimum Passed: "
            f"{'✅ YES' if one_dollar['meets_minimum'] else '❌ NO'}\n\n"

            f"$5 MARGIN TEST\n"
            f"Quantity: "
            f"{decimal_text(five_dollar['quantity'])} BTC\n"

            f"Minimum Passed: "
            f"{'✅ YES' if five_dollar['meets_minimum'] else '❌ NO'}\n\n"

            f"🛡 Hard execution lock active\n"
            f"⚠️ No live order was sent."
        )

        await send_telegram(
            telegram_message
        )


# ============================================================
# ERROR HANDLER
# ============================================================

async def main():
    try:

        await run_diagnostic()

    except Exception as exc:

        separator()

        error_message = (
            f"❌ MODULE {MODULE_NAME} ERROR\n"
            f"{SYMBOL}\n\n"
            f"{type(exc).__name__}: {exc}\n\n"
            f"🛡 Hard execution lock active\n"
            f"⚠️ No live order was sent."
        )

        log(error_message)

        separator()

        await send_telegram(
            error_message
        )

    # Keep Render process alive.
    # Prevents immediate exit/restart repeatedly
    # sending the same Telegram diagnostic.

    log("")
    log(
        "MODULE DIAGNOSTIC COMPLETE"
    )

    log(
        "PROCESS REMAINING ONLINE..."
    )

    while True:
        await asyncio.sleep(
            KEEP_ALIVE_SECONDS
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())
