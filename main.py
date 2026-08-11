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
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H"

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
# BASIC HELPERS
# ============================================================

def credentials_ready():

    return bool(
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    )


def telegram_ready():

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(message):

    if not telegram_ready():
        print("TELEGRAM CONFIG: MISSING")
        return

    try:

        bot = Bot(
            token=TELEGRAM_BOT_TOKEN
        )

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print("TELEGRAM MESSAGE SENT")

    except Exception as exc:

        print(
            "TELEGRAM ERROR:",
            exc,
        )


# ============================================================
# DECIMAL HELPERS
# ============================================================

def D(value, default="0"):

    try:

        return Decimal(
            str(value)
        )

    except Exception:

        return Decimal(
            default
        )


def decimal_places(value):

    value = D(value)

    exponent = value.as_tuple().exponent

    if exponent >= 0:

        return 0

    return abs(exponent)


def round_down(
    value,
    precision,
):

    value = D(value)

    step = Decimal(
        "1"
    ).scaleb(
        -precision
    )

    return value.quantize(
        step,
        rounding=ROUND_DOWN,
    )


def pretty_decimal(
    value,
    places=8,
):

    value = D(value)

    text = (
        f"{value:.{places}f}"
    )

    text = text.rstrip(
        "0"
    ).rstrip(
        "."
    )

    return text or "0"


# ============================================================
# WEEX V3 SIGNATURE
# ============================================================

def create_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    method = method.upper()

    if query_string:

        message = (
            str(timestamp)
            + method
            + request_path
            + "?"
            + query_string
            + body
        )

    else:

        message = (
            str(timestamp)
            + method
            + request_path
            + body
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


def authenticated_headers(
    method,
    request_path,
    query_string="",
    body="",
):

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = create_signature(
        timestamp=timestamp,
        method=method,
        request_path=request_path,
        query_string=query_string,
        body=body,
    )

    return {

        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            signature,

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",

        "User-Agent":
            "0F-4H-WEEX-BOT",
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

    url = (
        API_BASE_URL
        + request_path
    )

    async with session.get(
        url,
        params=params,
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"PUBLIC GET FAILED "
                f"{response.status}: "
                f"{text}"
            )

        return json.loads(
            text
        )


async def authenticated_get(
    session,
    request_path,
    params=None,
):

    params = params or {}

    query_string = urlencode(
        params
    )

    url = (
        API_BASE_URL
        + request_path
    )

    if query_string:

        url += (
            "?"
            + query_string
        )

    headers = authenticated_headers(
        method="GET",
        request_path=request_path,
        query_string=query_string,
    )

    async with session.get(
        url,
        headers=headers,
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"AUTH GET FAILED "
                f"{response.status}: "
                f"{text}"
            )

        return json.loads(
            text
        )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_account_balance(
    session,
):

    path = (
        "/capi/v3/account/balance"
    )

    data = await authenticated_get(
        session,
        path,
    )

    if not isinstance(
        data,
        list,
    ):

        raise RuntimeError(
            "Unexpected balance response"
        )

    for item in data:

        if (
            str(
                item.get(
                    "asset",
                    ""
                )
            ).upper()
            == "USDT"
        ):

            return item

    raise RuntimeError(
        "USDT balance not found"
    )


# ============================================================
# EXCHANGE CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):

    path = (
        "/capi/v3/market/exchangeInfo"
    )

    data = await public_get(
        session,
        path,
        {
            "symbol":
                SYMBOL
        },
    )

    symbols = data.get(
        "symbols",
        [],
    )

    for item in symbols:

        if (
            str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper()
            == SYMBOL
        ):

            return item

    raise RuntimeError(
        f"{SYMBOL} contract "
        f"information not found"
    )


# ============================================================
# SYMBOL ACCOUNT CONFIGURATION
# ============================================================

async def get_symbol_configuration(
    session,
):

    path = (
        "/capi/v3/account/symbolConfig"
    )

    data = await authenticated_get(
        session,
        path,
        {
            "symbol":
                SYMBOL
        },
    )

    if not isinstance(
        data,
        list,
    ):

        raise RuntimeError(
            "Unexpected symbol "
            "configuration response"
        )

    for item in data:

        if (
            str(
                item.get(
                    "symbol",
                    ""
                )
            ).upper()
            == SYMBOL
        ):

            return item

    raise RuntimeError(
        f"{SYMBOL} configuration "
        f"not found"
    )


# ============================================================
# LIVE MARKET PRICE
# ============================================================

async def get_live_price(
    session,
):

    path = (
        "/capi/v3/market/ticker/"
        "bookTicker"
    )

    data = await public_get(
        session,
        path,
        {
            "symbol":
                SYMBOL
        },
    )

    if isinstance(
        data,
        list,
    ):

        if not data:

            raise RuntimeError(
                "Ticker response empty"
            )

        ticker = data[0]

    elif isinstance(
        data,
        dict,
    ):

        ticker = data

    else:

        raise RuntimeError(
            "Unexpected ticker response"
        )

    bid = D(
        ticker.get(
            "bidPrice"
        )
    )

    ask = D(
        ticker.get(
            "askPrice"
        )
    )

    if bid <= 0 or ask <= 0:

        raise RuntimeError(
            "Invalid bid/ask price"
        )

    mid = (
        bid + ask
    ) / Decimal(
        "2"
    )

    return (
        bid,
        ask,
        mid,
    )


# ============================================================
# ORDER READINESS CALCULATION
# ============================================================

def calculate_readiness(
    available_balance,
    live_price,
    contract,
):

    quantity_precision = int(
        contract.get(
            "quantityPrecision",
            6,
        )
    )

    min_order_size = D(
        contract.get(
            "minOrderSize"
        )
    )

    max_order_size = D(
        contract.get(
            "maxOrderSize"
        )
    )

    market_open_limit = D(
        contract.get(
            "marketOpenLimitSize"
        )
    )

    min_leverage = D(
        contract.get(
            "minLeverage",
            1,
        )
    )

    exchange_max_leverage = D(
        contract.get(
            "maxLeverage",
            0,
        )
    )

    entry_margin = (
        available_balance
        * INITIAL_ENTRY_PERCENT
        / Decimal(
            "100"
        )
    )

    leveraged_notional = (
        entry_margin
        * LEVERAGE
    )

    raw_quantity = (
        leveraged_notional
        / live_price
    )

    quantity = round_down(
        raw_quantity,
        quantity_precision,
    )

    actual_notional = (
        quantity
        * live_price
    )

    actual_margin = (
        actual_notional
        / LEVERAGE
    )

    checks = {}

    checks[
        "entry_percent_valid"
    ] = (
        INITIAL_ENTRY_PERCENT
        > 0
        and INITIAL_ENTRY_PERCENT
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    checks[
        "leverage_above_min"
    ] = (
        LEVERAGE
        >= min_leverage
    )

    checks[
        "leverage_under_bot_max"
    ] = (
        LEVERAGE
        <= MAX_LEVERAGE
    )

    checks[
        "leverage_under_exchange_max"
    ] = (
        exchange_max_leverage <= 0
        or LEVERAGE
        <= exchange_max_leverage
    )

    checks[
        "quantity_positive"
    ] = (
        quantity > 0
    )

    checks[
        "meets_min_order"
    ] = (
        min_order_size <= 0
        or quantity
        >= min_order_size
    )

    checks[
        "below_max_order"
    ] = (
        max_order_size <= 0
        or quantity
        <= max_order_size
    )

    checks[
        "below_market_open_limit"
    ] = (
        market_open_limit <= 0
        or quantity
        <= market_open_limit
    )

    checks[
        "margin_within_balance"
    ] = (
        actual_margin
        <= available_balance
    )

    readiness_passed = all(
        checks.values()
    )

    return {

        "entry_margin":
            entry_margin,

        "leveraged_notional":
            leveraged_notional,

        "raw_quantity":
            raw_quantity,

        "quantity":
            quantity,

        "actual_notional":
            actual_notional,

        "actual_margin":
            actual_margin,

        "quantity_precision":
            quantity_precision,

        "min_order_size":
            min_order_size,

        "max_order_size":
            max_order_size,

        "market_open_limit":
            market_open_limit,

        "min_leverage":
            min_leverage,

        "exchange_max_leverage":
            exchange_max_leverage,

        "checks":
            checks,

        "passed":
            readiness_passed,
    }


# ============================================================
# READINESS TEST
# ============================================================

async def run_readiness_test():

    print(
        "=" * 60
    )

    print(
        f"MODULE {MODULE_NAME} STARTING"
    )

    print(
        "WEEX LIVE ACCOUNT "
        "READINESS VERIFICATION"
    )

    print(
        SYMBOL
    )

    print(
        "=" * 60
    )

    print(
        f"Initial Entry: "
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    print(
        f"Leverage: "
        f"{LEVERAGE}x"
    )

    print(
        f"Bot Max Leverage: "
        f"{MAX_LEVERAGE}x"
    )

    print(
        f"Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    print(
        "LIVE ORDER EXECUTION: "
        "DISABLED"
    )

    print(
        "HARD EXECUTION LOCK: "
        "ACTIVE"
    )

    print(
        "=" * 60
    )

    if not credentials_ready():

        print(
            "WEEX CREDENTIALS: MISSING"
        )

        await send_telegram(
            "❌ MODULE 0F-4H FAILED\n"
            "BTCUSDT\n\n"
            "WEEX credentials missing.\n"
            "🛡 Hard execution lock active\n"
            "⚠️ No live order was sent."
        )

        return

    print(
        "WEEX CREDENTIALS: READY"
    )

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:

            print(
                "CHECK 1: "
                "ACCOUNT BALANCE"
            )

            balance = (
                await get_account_balance(
                    session
                )
            )

            total_balance = D(
                balance.get(
                    "balance"
                )
            )

            available_balance = D(
                balance.get(
                    "availableBalance"
                )
            )

            frozen = D(
                balance.get(
                    "frozen"
                )
            )

            unrealized_pnl = D(
                balance.get(
                    "unrealizePnl"
                )
            )

            print(
                "✅ AUTHENTICATED "
                "ACCOUNT ACCESS"
            )

            print(
                "USDT TOTAL BALANCE:",
                pretty_decimal(
                    total_balance
                ),
            )

            print(
                "USDT AVAILABLE:",
                pretty_decimal(
                    available_balance
                ),
            )

            print(
                "USDT FROZEN:",
                pretty_decimal(
                    frozen
                ),
            )

            print(
                "UNREALIZED PNL:",
                pretty_decimal(
                    unrealized_pnl
                ),
            )

            print(
                "-" * 60
            )

            print(
                "CHECK 2: "
                "BTCUSDT CONTRACT"
            )

            contract = (
                await get_contract_info(
                    session
                )
            )

            print(
                "✅ CONTRACT FOUND"
            )

            print(
                "MIN ORDER SIZE:",
                contract.get(
                    "minOrderSize"
                ),
            )

            print(
                "MAX ORDER SIZE:",
                contract.get(
                    "maxOrderSize"
                ),
            )

            print(
                "QUANTITY PRECISION:",
                contract.get(
                    "quantityPrecision"
                ),
            )

            print(
                "MIN LEVERAGE:",
                contract.get(
                    "minLeverage"
                ),
            )

            print(
                "MAX LEVERAGE:",
                contract.get(
                    "maxLeverage"
                ),
            )

            print(
                "-" * 60
            )

            print(
                "CHECK 3: "
                "ACCOUNT SYMBOL CONFIG"
            )

            symbol_config = (
                await
                get_symbol_configuration(
                    session
                )
            )

            margin_type = (
                symbol_config.get(
                    "marginType",
                    "UNKNOWN",
                )
            )

            separated_type = (
                symbol_config.get(
                    "separatedType",
                    "UNKNOWN",
                )
            )

            cross_leverage = (
                symbol_config.get(
                    "crossLeverage",
                    "UNKNOWN",
                )
            )

            isolated_long = (
                symbol_config.get(
                    "isolatedLongLeverage",
                    "UNKNOWN",
                )
            )

            isolated_short = (
                symbol_config.get(
                    "isolatedShortLeverage",
                    "UNKNOWN",
                )
            )

            print(
                "✅ SYMBOL CONFIG "
                "RECEIVED"
            )

            print(
                "MARGIN MODE:",
                margin_type,
            )

            print(
                "POSITION MODE:",
                separated_type,
            )

            print(
                "CROSS LEVERAGE:",
                cross_leverage,
            )

            print(
                "ISOLATED LONG LEVERAGE:",
                isolated_long,
            )

            print(
                "ISOLATED SHORT LEVERAGE:",
                isolated_short,
            )

            print(
                "-" * 60
            )

            print(
                "CHECK 4: "
                "LIVE MARKET PRICE"
            )

            (
                bid,
                ask,
                mid,
            ) = await get_live_price(
                session
            )

            print(
                "✅ LIVE PRICE RECEIVED"
            )

            print(
                "BID:",
                pretty_decimal(
                    bid,
                    2,
                ),
            )

            print(
                "ASK:",
                pretty_decimal(
                    ask,
                    2,
                ),
            )

            print(
                "CALCULATION PRICE:",
                pretty_decimal(
                    mid,
                    2,
                ),
            )

            print(
                "-" * 60
            )

            print(
                "CHECK 5: "
                "PLANNED ORDER "
                "CALCULATION"
            )

            readiness = (
                calculate_readiness(
                    available_balance=
                        available_balance,

                    live_price=
                        mid,

                    contract=
                        contract,
                )
            )

            print(
                "ENTRY MARGIN:",
                pretty_decimal(
                    readiness[
                        "entry_margin"
                    ]
                ),
                "USDT",
            )

            print(
                "LEVERAGED NOTIONAL:",
                pretty_decimal(
                    readiness[
                        "leveraged_notional"
                    ]
                ),
                "USDT",
            )

            print(
                "CALCULATED QUANTITY:",
                pretty_decimal(
                    readiness[
                        "quantity"
                    ]
                ),
                "BTC",
            )

            print(
                "ACTUAL ORDER NOTIONAL:",
                pretty_decimal(
                    readiness[
                        "actual_notional"
                    ]
                ),
                "USDT",
            )

            print(
                "ESTIMATED MARGIN USED:",
                pretty_decimal(
                    readiness[
                        "actual_margin"
                    ]
                ),
                "USDT",
            )

            print(
                "-" * 60
            )

            print(
                "SAFETY VALIDATION"
            )

            for (
                name,
                passed,
            ) in readiness[
                "checks"
            ].items():

                icon = (
                    "✅"
                    if passed
                    else "❌"
                )

                print(
                    icon,
                    name.upper(),
                )

            print(
                "=" * 60
            )

            if readiness[
                "passed"
            ]:

                print(
                    "MODULE 0F-4H: PASSED"
                )

                print(
                    "✅ ACCOUNT READINESS "
                    "VERIFIED"
                )

                print(
                    "✅ ORDER SIZE "
                    "CALCULATION VALID"
                )

                print(
                    "🛡 HARD EXECUTION "
                    "LOCK ACTIVE"
                )

                print(
                    "⚠️ NO LIVE ORDER "
                    "WAS SENT"
                )

                message = (
                    "✅ MODULE 0F-4H PASSED\n"
                    "BTCUSDT\n\n"

                    "Live Account Readiness "
                    "Verification\n\n"

                    "✅ WEEX authentication\n"
                    "✅ Account balance read\n"
                    "✅ Contract limits read\n"
                    "✅ Symbol configuration read\n"
                    "✅ Live market price read\n"
                    "✅ Order size calculation\n"
                    "✅ Safety validation\n\n"

                    f"Available USDT: "
                    f"{pretty_decimal(available_balance)}\n"

                    f"Entry: "
                    f"{INITIAL_ENTRY_PERCENT}%\n"

                    f"Leverage: "
                    f"{LEVERAGE}x\n"

                    f"Planned Margin: "
                    f"{pretty_decimal(readiness['actual_margin'])} "
                    f"USDT\n"

                    f"Planned Quantity: "
                    f"{pretty_decimal(readiness['quantity'])} "
                    f"BTC\n"

                    f"Approx Notional: "
                    f"{pretty_decimal(readiness['actual_notional'])} "
                    f"USDT\n\n"

                    f"Margin Mode: "
                    f"{margin_type}\n"

                    f"Position Mode: "
                    f"{separated_type}\n\n"

                    "🛡 Hard execution lock active\n"
                    "⚠️ Live order execution disabled\n"
                    "⚠️ No live order was sent."
                )

            else:

                print(
                    "MODULE 0F-4H: "
                    "READINESS CHECK FAILED"
                )

                print(
                    "🛡 HARD EXECUTION "
                    "LOCK REMAINS ACTIVE"
                )

                print(
                    "⚠️ NO LIVE ORDER "
                    "WAS SENT"
                )

                failed_checks = [

                    name

                    for (
                        name,
                        passed,
                    ) in readiness[
                        "checks"
                    ].items()

                    if not passed

                ]

                message = (
                    "⚠️ MODULE 0F-4H "
                    "NOT READY\n"
                    "BTCUSDT\n\n"

                    "Failed checks:\n"
                    + "\n".join(
                        f"❌ {x}"
                        for x
                        in failed_checks
                    )
                    + "\n\n"
                    "🛡 Hard execution lock active\n"
                    "⚠️ No live order was sent."
                )

            await send_telegram(
                message
            )

        except Exception as exc:

            print(
                "=" * 60
            )

            print(
                "MODULE 0F-4H ERROR"
            )

            print(
                type(
                    exc
                ).__name__,
                ":",
                exc,
            )

            print(
                "🛡 HARD EXECUTION "
                "LOCK ACTIVE"
            )

            print(
                "⚠️ NO LIVE ORDER "
                "WAS SENT"
            )

            await send_telegram(
                "❌ MODULE 0F-4H ERROR\n"
                "BTCUSDT\n\n"
                f"{type(exc).__name__}: "
                f"{exc}\n\n"
                "🛡 Hard execution lock active\n"
                "⚠️ No live order was sent."
            )


# ============================================================
# MAIN
# ============================================================

async def main():

    await run_readiness_test()


if __name__ == "__main__":

    asyncio.run(
        main())
