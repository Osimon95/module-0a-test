import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, ROUND_DOWN

import aiohttp
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R4"

SYMBOL = "BTCUSDT"

API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# HARDCODED BTC TEST CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal("5")

LEVERAGE = Decimal("100")

MAX_LEVERAGE = Decimal("100")


# ============================================================
# ABSOLUTE SAFETY LOCKS
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True


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
# HELPERS
# ============================================================

def D(value):
    return Decimal(str(value))


def decimal_text(value):
    """
    Convert Decimal to normal non-scientific text.
    """
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_to_precision(value, precision):
    """
    Round DOWN to the number of decimal places accepted
    by the exchange.
    """

    precision = int(precision)

    step = Decimal("1").scaleb(-precision)

    return D(value).quantize(
        step,
        rounding=ROUND_DOWN,
    )


def bool_icon(value):
    return "✅ YES" if value else "❌ NO"


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("TELEGRAM CONFIG: MISSING")
        return

    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print("TELEGRAM MESSAGE SENT")

    except Exception as exc:
        print(
            "TELEGRAM ERROR:",
            type(exc).__name__,
            str(exc),
        )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def generate_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):
    """
    WEEX signature:
    timestamp + HTTP method + request path + query string + body
    """

    message = (
        str(timestamp)
        + method.upper()
        + request_path
        + query_string
        + body
    )

    signature = hmac.new(
        WEEX_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        signature
    ).decode()


# ============================================================
# PUBLIC GET REQUEST
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    url = API_BASE_URL + path

    async with session.get(
        url,
        params=params,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP {response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                f"WEEX PUBLIC INVALID JSON: {text}"
            )


# ============================================================
# AUTHENTICATED GET REQUEST
# ============================================================

async def private_get(
    session,
    path,
    query_string="",
):
    if not WEEX_API_KEY:
        raise RuntimeError(
            "WEEX_API_KEY is missing."
        )

    if not WEEX_API_SECRET:
        raise RuntimeError(
            "WEEX_API_SECRET is missing."
        )

    if not WEEX_API_PASSPHRASE:
        raise RuntimeError(
            "WEEX_API_PASSPHRASE is missing."
        )

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = generate_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
        body="",
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "locale": "en-US",
    }

    url = (
        API_BASE_URL
        + path
        + query_string
    )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=15),
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE HTTP {response.status}: {text}"
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            raise RuntimeError(
                f"WEEX PRIVATE INVALID JSON: {text}"
            )


# ============================================================
# GET AVAILABLE USDT
# ============================================================

async def get_available_usdt(session):

    path = "/capi/v3/account/balance"

    data = await private_get(
        session,
        path,
    )

    if not isinstance(data, list):
        raise RuntimeError(
            f"Unexpected WEEX balance response: {data}"
        )

    for asset in data:

        if (
            str(asset.get("asset", "")).upper()
            == "USDT"
        ):
            available = asset.get(
                "availableBalance"
            )

            if available is None:
                raise RuntimeError(
                    "USDT availableBalance missing."
                )

            return D(available)

    raise RuntimeError(
        "USDT balance not found."
    )


# ============================================================
# GET BTC CONTRACT INFORMATION
# ============================================================

async def get_contract_info(session):

    data = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    symbols = data.get("symbols", [])

    if not symbols:
        raise RuntimeError(
            f"No exchange information returned for {SYMBOL}."
        )

    for contract in symbols:

        if (
            str(contract.get("symbol", "")).upper()
            == SYMBOL
        ):
            return contract

    raise RuntimeError(
        f"{SYMBOL} not found in exchange information."
    )


# ============================================================
# GET REAL MARK PRICE
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

    price = data.get("price")

    if price is None:
        raise RuntimeError(
            f"MARK price missing: {data}"
        )

    price = D(price)

    if price <= 0:
        raise RuntimeError(
            f"Invalid MARK price: {price}"
        )

    return price


# ============================================================
# QUANTITY CALCULATION
# ============================================================

def calculate_quantity(
    margin,
    leverage,
    mark_price,
    quantity_precision,
):

    if margin <= 0:
        return Decimal("0")

    if leverage <= 0:
        return Decimal("0")

    if mark_price <= 0:
        return Decimal("0")

    notional = (
        margin
        * leverage
    )

    raw_quantity = (
        notional
        / mark_price
    )

    final_quantity = floor_to_precision(
        raw_quantity,
        quantity_precision,
    )

    return final_quantity


# ============================================================
# DIAGNOSTIC
# ============================================================

async def run_diagnostic():

    print("=" * 60)
    print(f"MODULE {MODULE_NAME} STARTING")
    print("BTCUSDT 100x SAFE SIZING DIAGNOSTIC")
    print("=" * 60)

    print(
        "Initial Entry:",
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    print(
        "Hardcoded Leverage:",
        f"{LEVERAGE}x"
    )

    print(
        "Configured Max Leverage:",
        f"{MAX_LEVERAGE}x"
    )

    print(
        "LIVE ORDER EXECUTION:",
        "ENABLED"
        if LIVE_ORDER_EXECUTION
        else "DISABLED"
    )

    print(
        "HARD EXECUTION LOCK:",
        "ACTIVE"
        if HARD_EXECUTION_LOCK
        else "INACTIVE"
    )

    print("=" * 60)

    async with aiohttp.ClientSession() as session:

        # ----------------------------------------------------
        # ACCOUNT BALANCE
        # ----------------------------------------------------

        available_usdt = await get_available_usdt(
            session
        )

        print(
            "AVAILABLE USDT:",
            decimal_text(available_usdt),
        )

        # ----------------------------------------------------
        # CONTRACT INFORMATION
        # ----------------------------------------------------

        contract = await get_contract_info(
            session
        )

        min_order_size = D(
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

        contract_value = D(
            contract.get(
                "contractVal",
                "0",
            )
        )

        exchange_min_leverage = D(
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

        print(
            "WEEX MINIMUM ORDER:",
            decimal_text(min_order_size),
            "BTC",
        )

        print(
            "QUANTITY PRECISION:",
            quantity_precision,
        )

        print(
            "CONTRACT VALUE:",
            decimal_text(contract_value),
        )

        print(
            "WEEX MIN LEVERAGE:",
            f"{exchange_min_leverage}x",
        )

        print(
            "WEEX MAX LEVERAGE:",
            f"{exchange_max_leverage}x",
        )

        # ----------------------------------------------------
        # REAL MARK PRICE
        # ----------------------------------------------------

        mark_price = await get_mark_price(
            session
        )

        print(
            "BTC MARK PRICE:",
            decimal_text(mark_price),
            "USDT",
        )

        print("=" * 60)

        # ----------------------------------------------------
        # LEVERAGE VALIDATION
        # ----------------------------------------------------

        leverage_above_exchange_min = (
            LEVERAGE >= exchange_min_leverage
        )

        leverage_below_exchange_max = (
            LEVERAGE <= exchange_max_leverage
        )

        leverage_passed = (
            leverage_above_exchange_min
            and leverage_below_exchange_max
        )

        print("100x LEVERAGE VALIDATION")

        print(
            "100x within WEEX range:",
            bool_icon(leverage_passed),
        )

        print("=" * 60)

        # ----------------------------------------------------
        # 5% ENTRY
        # ----------------------------------------------------

        entry_margin = (
            available_usdt
            * INITIAL_ENTRY_PERCENT
            / Decimal("100")
        )

        entry_notional = (
            entry_margin
            * LEVERAGE
        )

        raw_entry_quantity = (
            entry_notional
            / mark_price
        )

        entry_quantity = calculate_quantity(
            margin=entry_margin,
            leverage=LEVERAGE,
            mark_price=mark_price,
            quantity_precision=quantity_precision,
        )

        entry_passed = (
            entry_quantity
            >= min_order_size
            and entry_quantity > 0
        )

        print("CURRENT 5% ENTRY @ 100x")

        print(
            "Margin:",
            decimal_text(entry_margin),
            "USDT",
        )

        print(
            "Notional:",
            decimal_text(entry_notional),
            "USDT",
        )

        print(
            "Raw Quantity:",
            decimal_text(raw_entry_quantity),
            "BTC",
        )

        print(
            "Rounded Quantity:",
            decimal_text(entry_quantity),
            "BTC",
        )

        print(
            "Minimum Passed:",
            bool_icon(entry_passed),
        )

        print("=" * 60)

        # ----------------------------------------------------
        # TRUE MINIMUM MARGIN AT 100x
        # ----------------------------------------------------

        minimum_notional = (
            min_order_size
            * mark_price
        )

        minimum_margin_required = (
            minimum_notional
            / LEVERAGE
        )

        balance_sufficient_for_minimum = (
            available_usdt
            >= minimum_margin_required
        )

        five_percent_sufficient = (
            entry_margin
            >= minimum_margin_required
        )

        print("TRUE MINIMUM AT 100x")

        print(
            "Minimum Notional:",
            decimal_text(minimum_notional),
            "USDT",
        )

        print(
            "Minimum Margin Required:",
            decimal_text(
                minimum_margin_required
            ),
            "USDT",
        )

        print(
            "Account Balance Sufficient:",
            bool_icon(
                balance_sufficient_for_minimum
            ),
        )

        print(
            "5% Entry Margin Sufficient:",
            bool_icon(
                five_percent_sufficient
            ),
        )

        print("=" * 60)

        # ----------------------------------------------------
        # $1 MARGIN SIMULATION
        # ----------------------------------------------------

        one_dollar_margin = Decimal("1")

        one_dollar_quantity = calculate_quantity(
            margin=one_dollar_margin,
            leverage=LEVERAGE,
            mark_price=mark_price,
            quantity_precision=quantity_precision,
        )

        one_dollar_passed = (
            one_dollar_quantity
            >= min_order_size
        )

        print("$1 MARGIN TEST @ 100x")

        print(
            "Notional:",
            decimal_text(
                one_dollar_margin
                * LEVERAGE
            ),
            "USDT",
        )

        print(
            "Quantity:",
            decimal_text(
                one_dollar_quantity
            ),
            "BTC",
        )

        print(
            "Minimum Passed:",
            bool_icon(
                one_dollar_passed
            ),
        )

        print("=" * 60)

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        checks = {
            "credentials_ready": bool(
                WEEX_API_KEY
                and WEEX_API_SECRET
                and WEEX_API_PASSPHRASE
            ),

            "balance_positive":
                available_usdt > 0,

            "mark_price_positive":
                mark_price > 0,

            "min_order_positive":
                min_order_size > 0,

            "leverage_allowed":
                leverage_passed,

            "quantity_positive":
                entry_quantity > 0,

            "meets_min_order":
                entry_passed,

            "balance_sufficient_for_min_order":
                balance_sufficient_for_minimum,

            "five_percent_entry_sufficient":
                five_percent_sufficient,

            "hard_execution_lock":
                HARD_EXECUTION_LOCK,

            "live_execution_disabled":
                not LIVE_ORDER_EXECUTION,
        }

        failed_checks = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        diagnostic_passed = (
            len(failed_checks) == 0
        )

        if diagnostic_passed:

            title = (
                f"✅ MODULE {MODULE_NAME} "
                "DIAGNOSTIC PASSED"
            )

        else:

            title = (
                f"⚠️ MODULE {MODULE_NAME} "
                "NOT READY"
            )

        message_lines = [
            title,
            "",
            SYMBOL,
            "",
            f"Available USDT: "
            f"{decimal_text(available_usdt)}",
            "",
            "HARDCODED TEST CONFIG",
            f"Entry: {INITIAL_ENTRY_PERCENT}%",
            f"Leverage: {LEVERAGE}x",
            "",
            "WEEX CONTRACT",
            f"Mark Price: "
            f"{decimal_text(mark_price)} USDT",
            f"Minimum Order: "
            f"{decimal_text(min_order_size)} BTC",
            f"Quantity Precision: "
            f"{quantity_precision}",
            f"Contract Value: "
            f"{decimal_text(contract_value)}",
            f"WEEX Max Leverage: "
            f"{decimal_text(exchange_max_leverage)}x",
            "",
            "100x VALIDATION",
            f"Allowed by WEEX: "
            f"{bool_icon(leverage_passed)}",
            "",
            "CURRENT 5% ENTRY",
            f"Margin: "
            f"{decimal_text(entry_margin)} USDT",
            f"Notional: "
            f"{decimal_text(entry_notional)} USDT",
            f"Quantity: "
            f"{decimal_text(entry_quantity)} BTC",
            f"Minimum Passed: "
            f"{bool_icon(entry_passed)}",
            "",
            "TRUE MINIMUM AT 100x",
            f"Minimum Notional: "
            f"{decimal_text(minimum_notional)} USDT",
            f"Minimum Margin Required: "
            f"{decimal_text(minimum_margin_required)} USDT",
            f"5% Entry Sufficient: "
            f"{bool_icon(five_percent_sufficient)}",
            "",
            "$1 MARGIN TEST",
            f"Quantity: "
            f"{decimal_text(one_dollar_quantity)} BTC",
            f"Minimum Passed: "
            f"{bool_icon(one_dollar_passed)}",
        ]

        if failed_checks:

            message_lines.extend([
                "",
                "FAILED CHECKS:",
            ])

            for check in failed_checks:
                message_lines.append(
                    f"❌ {check}"
                )

        message_lines.extend([
            "",
            "🛡 Hard execution lock active",
            "⚠️ Live order execution disabled",
            "⚠️ NO LIVE ORDER WAS SENT",
        ])

        telegram_message = "\n".join(
            message_lines
        )

        print(telegram_message)

        await send_telegram(
            telegram_message
        )

        print("=" * 60)
        print("DIAGNOSTIC COMPLETE")
        print("NO LIVE ORDER WAS SENT")
        print("=" * 60)


# ============================================================
# MAIN
# ============================================================

async def main():

    try:

        await run_diagnostic()

    except Exception as exc:

        error_message = (
            f"❌ MODULE {MODULE_NAME} ERROR\n\n"
            f"{SYMBOL}\n\n"
            f"{type(exc).__name__}: {exc}\n\n"
            "🛡 Hard execution lock active\n"
            "⚠️ No live order was sent."
        )

        print(error_message)

        await send_telegram(
            error_message
        )


if __name__ == "__main__":
    asyncio.run(main())
