import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, ROUND_DOWN, ROUND_CEILING
from urllib.parse import urlencode

import aiohttp
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R2"

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
# SAFETY LOCKS
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
# DECIMAL HELPERS
# ============================================================

def D(value, default="0"):

    try:

        return Decimal(str(value))

    except Exception:

        return Decimal(default)


def fmt(value, places=8):

    value = D(value)

    text = f"{value:.{places}f}"

    text = text.rstrip("0").rstrip(".")

    return text or "0"


def floor_to_precision(value, precision):

    step = Decimal("1").scaleb(
        -int(precision)
    )

    return D(value).quantize(
        step,
        rounding=ROUND_DOWN,
    )


def ceil_integer(value):

    return int(
        D(value).to_integral_value(
            rounding=ROUND_CEILING
        )
    )


# ============================================================
# WEEX SIGNATURE
# ============================================================

def create_signature(
    timestamp,
    method,
    path,
    query_string="",
    body="",
):

    if query_string:

        message = (
            f"{timestamp}"
            f"{method.upper()}"
            f"{path}"
            f"?"
            f"{query_string}"
            f"{body}"
        )

    else:

        message = (
            f"{timestamp}"
            f"{method.upper()}"
            f"{path}"
            f"{body}"
        )

    digest = hmac.new(
        WEEX_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode("utf-8")


# ============================================================
# PUBLIC GET
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):

    async with session.get(
        API_BASE_URL + path,
        params=params or {},
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text[:500]}"
            )

        return json.loads(text)


# ============================================================
# PRIVATE AUTHENTICATED GET
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):

    params = params or {}

    query_string = urlencode(params)

    timestamp = str(
        int(time.time() * 1000)
    )

    signature = create_signature(
        timestamp=timestamp,
        method="GET",
        path=path,
        query_string=query_string,
    )

    headers = {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-TIMESTAMP":
            timestamp,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "Content-Type":
            "application/json",
    }

    url = (
        API_BASE_URL
        + path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(
            total=15
        ),
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX PRIVATE HTTP "
                f"{response.status}: "
                f"{text[:500]}"
            )

        return json.loads(text)


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):

    payload = await public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol":
                SYMBOL
        },
    )

    symbols = payload.get(
        "symbols",
        [],
    )

    for item in symbols:

        if (
            str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ):

            return item

    raise RuntimeError(
        f"{SYMBOL} not found "
        f"in WEEX exchangeInfo"
    )


# ============================================================
# LIVE BTC PRICE
# ============================================================

async def get_price(
    session,
):

    payload = await public_get(
        session,
        "/capi/v3/market/ticker/price",
        {
            "symbol":
                SYMBOL
        },
    )

    if isinstance(
        payload,
        list,
    ):

        for item in payload:

            if (
                str(
                    item.get(
                        "symbol",
                        "",
                    )
                ).upper()
                == SYMBOL
            ):

                return D(
                    item.get(
                        "price"
                    )
                )

    if isinstance(
        payload,
        dict,
    ):

        price = D(
            payload.get(
                "price"
            )
        )

        if price > 0:

            return price

    raise RuntimeError(
        "Unable to read "
        "BTCUSDT price"
    )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session,
):

    balances = await private_get(
        session,
        "/capi/v3/account/balance",
    )

    if not isinstance(
        balances,
        list,
    ):

        raise RuntimeError(
            "Unexpected WEEX "
            "balance response"
        )

    for item in balances:

        if (
            str(
                item.get(
                    "asset",
                    "",
                )
            ).upper()
            == "USDT"
        ):

            return D(
                item.get(
                    "availableBalance"
                )
            )

    raise RuntimeError(
        "USDT balance "
        "not found"
    )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    message,
):

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        print(
            "TELEGRAM CONFIG: MISSING"
        )

        return

    try:

        bot = Bot(
            token=
            TELEGRAM_BOT_TOKEN
        )

        await bot.send_message(
            chat_id=
                TELEGRAM_CHAT_ID,
            text=
                message,
        )

        print(
            "TELEGRAM MESSAGE SENT"
        )

    except Exception as exc:

        print(
            "TELEGRAM ERROR:",
            exc,
        )


# ============================================================
# LOCAL CONFIG VALIDATION
# ============================================================

def validate_configuration():

    errors = []

    if INITIAL_ENTRY_PERCENT <= 0:

        errors.append(
            "INITIAL_ENTRY_PERCENT "
            "must be greater than 0"
        )

    if (
        INITIAL_ENTRY_PERCENT
        >
        MAX_FUND_EXPOSURE_PERCENT
    ):

        errors.append(
            "INITIAL_ENTRY_PERCENT "
            "exceeds "
            "MAX_FUND_EXPOSURE_PERCENT"
        )

    if LEVERAGE <= 0:

        errors.append(
            "LEVERAGE must be "
            "greater than 0"
        )

    if (
        LEVERAGE
        >
        MAX_LEVERAGE
    ):

        errors.append(
            "LEVERAGE exceeds "
            "MAX_LEVERAGE"
        )

    if (
        not WEEX_API_KEY
        or not WEEX_API_SECRET
        or not WEEX_API_PASSPHRASE
    ):

        errors.append(
            "WEEX credentials "
            "are missing"
        )

    return errors


# ============================================================
# READINESS CHECK
# ============================================================

async def readiness_check():

    print(
        "=" * 60
    )

    print(
        f"MODULE "
        f"{MODULE_NAME} "
        f"STARTING"
    )

    print(
        "WEEX MINIMUM-ORDER-AWARE "
        "READINESS VERIFICATION"
    )

    print(
        SYMBOL
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # LOCAL CONFIG
    # --------------------------------------------------------

    errors = (
        validate_configuration()
    )

    if errors:

        print(
            "CONFIGURATION ERROR"
        )

        for error in errors:

            print(
                "ERROR:",
                error,
            )

        message = (
            f"⚠️ MODULE "
            f"{MODULE_NAME} "
            f"CONFIG ERROR\n"
            f"{SYMBOL}\n\n"
        )

        for error in errors:

            message += (
                f"❌ {error}\n"
            )

        message += (
            "\n"
            "🛡 Hard execution "
            "lock active\n"
            "⚠️ No live order "
            "was sent."
        )

        await send_telegram(
            message
        )

        return


    # --------------------------------------------------------
    # LIVE DATA
    # --------------------------------------------------------

    async with (
        aiohttp.ClientSession()
        as session
    ):

        contract = (
            await get_contract_info(
                session
            )
        )

        price = (
            await get_price(
                session
            )
        )

        available = (
            await get_available_usdt(
                session
            )
        )


    # --------------------------------------------------------
    # CONTRACT SETTINGS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # OUR ENTRY CALCULATION
    # --------------------------------------------------------

    entry_fraction = (
        INITIAL_ENTRY_PERCENT
        /
        Decimal("100")
    )

    allocated_margin = (
        available
        *
        entry_fraction
    )

    target_notional = (
        allocated_margin
        *
        LEVERAGE
    )


    # --------------------------------------------------------
    # BTC QUANTITY
    # --------------------------------------------------------

    if price > 0:

        raw_quantity = (
            target_notional
            /
            price
        )

    else:

        raw_quantity = (
            Decimal("0")
        )

    calculated_quantity = (
        floor_to_precision(
            raw_quantity,
            quantity_precision,
        )
    )


    # --------------------------------------------------------
    # WEEX MINIMUM POSITION VALUE
    # --------------------------------------------------------

    minimum_notional = (
        min_order_size
        *
        price
    )


    # --------------------------------------------------------
    # MARGIN REQUIRED AT OUR CURRENT LEVERAGE
    # --------------------------------------------------------

    if LEVERAGE > 0:

        minimum_margin = (
            minimum_notional
            /
            LEVERAGE
        )

    else:

        minimum_margin = (
            Decimal("0")
        )


    # --------------------------------------------------------
    # BALANCE NEEDED IF WE INSIST ON 5% ENTRY
    # --------------------------------------------------------

    if entry_fraction > 0:

        minimum_balance = (
            minimum_margin
            /
            entry_fraction
        )

    else:

        minimum_balance = (
            Decimal("0")
        )


    # --------------------------------------------------------
    # WHAT WOULD A $1 MARGIN TRADE REQUIRE?
    # --------------------------------------------------------

    if minimum_notional > 0:

        leverage_for_one_usdt = (
            ceil_integer(
                minimum_notional
                /
                Decimal("1")
            )
        )

    else:

        leverage_for_one_usdt = 0


    # --------------------------------------------------------
    # CHECKS
    # --------------------------------------------------------

    checks = {

        "price_positive":
            price > 0,

        "balance_positive":
            available > 0,

        "quantity_positive":
            calculated_quantity > 0,

        "meets_min_order":
            calculated_quantity
            >=
            min_order_size,

        "exchange_leverage_valid":
            (
                LEVERAGE
                >=
                exchange_min_leverage
                and
                (
                    exchange_max_leverage
                    <= 0
                    or
                    LEVERAGE
                    <=
                    exchange_max_leverage
                )
            ),

        "hard_lock_active":
            HARD_EXECUTION_LOCK,

        "live_execution_disabled":
            not LIVE_ORDER_EXECUTION,
    }


    ready_for_min_order = all(
        [
            checks[
                "price_positive"
            ],
            checks[
                "balance_positive"
            ],
            checks[
                "quantity_positive"
            ],
            checks[
                "meets_min_order"
            ],
            checks[
                "exchange_leverage_valid"
            ],
        ]
    )


    # --------------------------------------------------------
    # RENDER LOG
    # --------------------------------------------------------

    print(
        f"Available USDT: "
        f"{fmt(available, 4)}"
    )

    print(
        f"BTC Price: "
        f"{fmt(price, 2)}"
    )

    print(
        f"Initial Entry: "
        f"{fmt(INITIAL_ENTRY_PERCENT, 2)}%"
    )

    print(
        f"Allocated Margin: "
        f"{fmt(allocated_margin, 6)} "
        f"USDT"
    )

    print(
        f"Leverage: "
        f"{fmt(LEVERAGE, 2)}x"
    )

    print(
        f"Target Position Notional: "
        f"{fmt(target_notional, 6)} "
        f"USDT"
    )

    print(
        f"Raw BTC Quantity: "
        f"{fmt(raw_quantity, 10)}"
    )

    print(
        f"Rounded BTC Quantity: "
        f"{fmt(calculated_quantity, 10)}"
    )

    print(
        f"WEEX Quantity Precision: "
        f"{quantity_precision}"
    )

    print(
        f"WEEX Contract Value: "
        f"{fmt(contract_value, 10)} "
        f"BTC"
    )

    print(
        f"WEEX Minimum Order: "
        f"{fmt(min_order_size, 10)} "
        f"BTC"
    )

    print(
        f"Minimum Order Notional: "
        f"{fmt(minimum_notional, 6)} "
        f"USDT"
    )

    print(
        f"Minimum Margin Needed "
        f"At {fmt(LEVERAGE, 2)}x: "
        f"{fmt(minimum_margin, 6)} "
        f"USDT"
    )

    print(
        f"Minimum Account Balance "
        f"At "
        f"{fmt(INITIAL_ENTRY_PERCENT, 2)}% "
        f"Entry: "
        f"{fmt(minimum_balance, 6)} "
        f"USDT"
    )

    print(
        "Approximate Leverage Needed "
        "For $1 Margin: "
        f"{leverage_for_one_usdt}x"
    )

    print(
        "-" * 60
    )

    for (
        check_name,
        passed,
    ) in checks.items():

        if passed:

            print(
                f"PASS: "
                f"{check_name}"
            )

        else:

            print(
                f"FAIL: "
                f"{check_name}"
            )


    # --------------------------------------------------------
    # TELEGRAM STATUS
    # --------------------------------------------------------

    if ready_for_min_order:

        status_icon = "✅"

        status_text = "READY"

        sizing_text = (
            "✅ Minimum order "
            "sizing passes"
        )

    else:

        status_icon = "⚠️"

        status_text = (
            "NOT READY"
        )

        sizing_text = (
            "❌ Current percentage "
            "sizing is below "
            "WEEX minimum"
        )


    message = (

        f"{status_icon} "
        f"MODULE "
        f"{MODULE_NAME} "
        f"{status_text}\n"

        f"{SYMBOL}\n\n"

        f"Available USDT: "
        f"{fmt(available, 4)}\n"

        f"BTC Price: "
        f"{fmt(price, 2)}\n"

        f"Entry: "
        f"{fmt(INITIAL_ENTRY_PERCENT, 2)}%\n"

        f"Allocated Margin: "
        f"{fmt(allocated_margin, 4)} "
        f"USDT\n"

        f"Leverage: "
        f"{fmt(LEVERAGE, 2)}x\n"

        f"Target Notional: "
        f"{fmt(target_notional, 4)} "
        f"USDT\n"

        f"Calculated Quantity: "
        f"{fmt(calculated_quantity, 10)} "
        f"BTC\n"

        f"WEEX Minimum: "
        f"{fmt(min_order_size, 10)} "
        f"BTC\n"

        f"Minimum Notional: "
        f"{fmt(minimum_notional, 4)} "
        f"USDT\n"

        f"Minimum Margin @ "
        f"{fmt(LEVERAGE, 2)}x: "
        f"{fmt(minimum_margin, 4)} "
        f"USDT\n"

        f"Minimum Balance @ "
        f"{fmt(INITIAL_ENTRY_PERCENT, 2)}% "
        f"entry: "
        f"{fmt(minimum_balance, 4)} "
        f"USDT\n"

        f"Approx. leverage for "
        f"$1 margin: "
        f"{leverage_for_one_usdt}x\n\n"

        f"{sizing_text}\n"

        f"🛡 Hard execution "
        f"lock active\n"

        f"⚠️ No live order "
        f"was sent."
    )

    await send_telegram(
        message
    )


    # --------------------------------------------------------
    # FINAL LOG
    # --------------------------------------------------------

    print(
        "=" * 60
    )

    print(
        "0F-4H-R2 READINESS "
        "CHECK COMPLETE"
    )

    print(
        "NO LIVE ORDERS "
        "WERE SENT"
    )

    print(
        "PROCESS REMAINS ALIVE"
    )

    print(
        "=" * 60
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    try:

        await readiness_check()

    except Exception as exc:

        print(
            f"0F-4H-R2 ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        await send_telegram(

            f"❌ MODULE "
            f"{MODULE_NAME} ERROR\n"

            f"{SYMBOL}\n\n"

            f"{type(exc).__name__}: "
            f"{exc}\n\n"

            f"🛡 Hard execution "
            f"lock active\n"

            f"⚠️ No live order "
            f"was sent."
        )


    # ========================================================
    # KEEP RENDER PROCESS ALIVE
    #
    # Prevents startup/restart loops from repeatedly sending
    # the same Telegram readiness report.
    # ========================================================

    while True:

        await asyncio.sleep(
            3600
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
