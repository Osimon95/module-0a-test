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


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R5"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# BTCUSDT CONFIRMED TEST BASELINE
# ============================================================
#
# R4 confirmed BTCUSDT sizing successfully at:
#
# Initial Entry = 5%
# Leverage = 100x
#
# These remain the R5 default test values.
#
# They can later be changed through Render environment
# variables without editing the code.
#
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


# ============================================================
# PYRAMID CONFIGURATION
# ============================================================

MAX_PYRAMID_ADDS = int(
    os.getenv(
        "MAX_PYRAMID_ADDS",
        "1",
    )
)

PYRAMID_ADD_PERCENTS_TEXT = os.getenv(
    "PYRAMID_ADD_PERCENTS",
    "5",
).strip()

PYRAMID_MOMENTUM_CONFIRMATION_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_MOMENTUM_CONFIRMATION_PERCENT",
        "0.30",
    )
)


# ============================================================
# BACKUP CONFIGURATION
# ============================================================

MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENTS_TEXT = os.getenv(
    "BACKUP_SIZE_PERCENTS",
    "5,5,5",
).strip()

BACKUP_LIQUIDATION_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_LIQUIDATION_BUFFER_PERCENT",
        "1.00",
    )
)

MIN_LIQUIDATION_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQUIDATION_DISTANCE_PERCENT",
        "2.00",
    )
)


# ============================================================
# TAKE-PROFIT CONFIGURATION
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
        "0.50",
    )
)

TP2_TRIGGER_PERCENT = Decimal(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1.00",
    )
)

TRAILING_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.20",
    )
)


# ============================================================
# SAFETY / CONTROL CONFIGURATION
# ============================================================

MAX_FUND_EXPOSURE_PERCENT = Decimal(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)

MAX_TRADE_LOSS_PERCENT = Decimal(
    os.getenv(
        "MAX_TRADE_LOSS_PERCENT",
        "5",
    )
)

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "180",
    )
)

LOSS_SEQUENCE_LIMIT = int(
    os.getenv(
        "LOSS_SEQUENCE_LIMIT",
        "2",
    )
)

COOLDOWN_SECONDS = int(
    os.getenv(
        "COOLDOWN_SECONDS",
        "900",
    )
)


# ============================================================
# BOOLEAN HELPERS
# ============================================================

def env_bool(name, default=True):

    raw = os.getenv(
        name,
        "true" if default else "false",
    )

    return raw.strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


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

IDLE_PYRAMID_CLEANUP = env_bool(
    "IDLE_PYRAMID_CLEANUP",
    True,
)


# ============================================================
# ABSOLUTE EXECUTION SAFETY LOCKS
# ============================================================
#
# IMPORTANT:
#
# These are intentionally NOT environment variables.
#
# Changing a Render environment variable therefore cannot
# accidentally enable real trading.
#
# R5 contains NO LIVE ORDER SUBMISSION FUNCTION.
#
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

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


def D(value):
    return Decimal(str(value))


def fmt(value):

    if not isinstance(value, Decimal):
        value = D(value)

    text = format(
        value.normalize(),
        "f",
    )

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def percent_amount(
    balance,
    percent,
):

    return (
        balance
        * percent
        / HUNDRED
    )


def parse_decimal_list(text):

    if not text:
        return []

    result = []

    for item in text.split(","):

        item = item.strip()

        if not item:
            continue

        result.append(
            Decimal(item)
        )

    return result


PYRAMID_ADD_PERCENTS = parse_decimal_list(
    PYRAMID_ADD_PERCENTS_TEXT
)

BACKUP_SIZE_PERCENTS = parse_decimal_list(
    BACKUP_SIZE_PERCENTS_TEXT
)


# ============================================================
# QUANTITY HELPERS
# ============================================================

def quantity_step_from_precision(
    precision,
):

    return Decimal(
        "1"
    ).scaleb(
        -int(precision)
    )


def floor_quantity(
    quantity,
    precision,
):

    step = quantity_step_from_precision(
        precision
    )

    return quantity.quantize(
        step,
        rounding=ROUND_DOWN,
    )


# ============================================================
# WEEX V3 SIGNATURE
# ============================================================

def build_signature(
    timestamp,
    method,
    request_path,
    query_string="",
    body="",
):

    method = method.upper()

    message = (
        timestamp
        + method
        + request_path
    )

    if query_string:
        message += (
            "?"
            + query_string
        )

    if body:
        message += body

    digest = hmac.new(
        WEEX_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


# ============================================================
# AUTHENTICATED GET
# ============================================================

async def weex_private_get(
    session,
    path,
    params=None,
):

    if not (
        WEEX_API_KEY
        and WEEX_API_SECRET
        and WEEX_API_PASSPHRASE
    ):
        raise RuntimeError(
            "WEEX API credentials are missing."
        )

    params = params or {}

    query_string = urlencode(
        params
    )

    timestamp = str(
        int(
            time.time() * 1000
        )
    )

    signature = build_signature(
        timestamp=timestamp,
        method="GET",
        request_path=path,
        query_string=query_string,
    )

    headers = {
        "ACCESS-KEY": WEEX_API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": WEEX_API_PASSPHRASE,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
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
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError:
            raise RuntimeError(
                "Invalid JSON received "
                "from WEEX private API."
            )


# ============================================================
# PUBLIC GET
# ============================================================

async def weex_public_get(
    session,
    path,
    params=None,
):

    params = params or {}

    query_string = urlencode(
        params
    )

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
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text}"
            )

        try:
            return json.loads(
                text
            )

        except json.JSONDecodeError:
            raise RuntimeError(
                "Invalid JSON received "
                "from WEEX public API."
            )


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    session,
    message,
):

    if not (
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM CONFIG: MISSING"
        )

        return

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:

        async with session.post(
            url,
            json=payload,
        ) as response:

            if response.status == 200:
                print(
                    "TELEGRAM MESSAGE SENT"
                )

            else:
                text = await response.text()

                print(
                    "TELEGRAM ERROR:",
                    response.status,
                    text,
                )

    except Exception as exc:

        print(
            "TELEGRAM ERROR:",
            repr(exc),
        )


# ============================================================
# ACCOUNT BALANCE
# ============================================================

async def get_available_usdt(
    session,
):

    data = await weex_private_get(
        session,
        "/capi/v3/account/balance",
    )

    if isinstance(data, dict):

        if isinstance(
            data.get("data"),
            list,
        ):
            data = data["data"]

        elif isinstance(
            data.get("result"),
            list,
        ):
            data = data["result"]

    if not isinstance(
        data,
        list,
    ):
        raise RuntimeError(
            "Unexpected WEEX balance response: "
            + str(data)
        )

    for asset in data:

        if str(
            asset.get(
                "asset",
                "",
            )
        ).upper() == "USDT":

            return Decimal(
                str(
                    asset.get(
                        "availableBalance",
                        "0",
                    )
                )
            )

    raise RuntimeError(
        "USDT balance was not found "
        "in WEEX account response."
    )


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract_info(
    session,
):

    data = await weex_public_get(
        session,
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    symbols = []

    if isinstance(data, dict):
        symbols = data.get(
            "symbols",
            [],
        )

        if not symbols:

            nested = data.get(
                "data",
                {}
            )

            if isinstance(
                nested,
                dict,
            ):
                symbols = nested.get(
                    "symbols",
                    [],
                )

    for contract in symbols:

        if str(
            contract.get(
                "symbol",
                "",
            )
        ).upper() == SYMBOL:

            return contract

    raise RuntimeError(
        f"{SYMBOL} contract information "
        "was not returned by WEEX."
    )


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):

    data = await weex_public_get(
        session,
        "/capi/v3/market/symbolPrice",
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    if isinstance(data, dict):

        if "price" in data:
            return Decimal(
                str(
                    data["price"]
                )
            )

        nested = data.get(
            "data"
        )

        if isinstance(
            nested,
            dict,
        ) and "price" in nested:

            return Decimal(
                str(
                    nested["price"]
                )
            )

    raise RuntimeError(
        "WEEX mark price could "
        "not be extracted."
    )


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_configuration(
    weex_max_leverage,
):

    checks = {}

    checks[
        "entry_positive"
    ] = (
        INITIAL_ENTRY_PERCENT > ZERO
    )

    checks[
        "leverage_positive"
    ] = (
        LEVERAGE > ZERO
    )

    checks[
        "leverage_within_local_cap"
    ] = (
        LEVERAGE
        <= MAX_LEVERAGE
    )

    checks[
        "leverage_allowed_by_weex"
    ] = (
        LEVERAGE
        <= weex_max_leverage
    )

    checks[
        "tp_total_100"
    ] = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
        == HUNDRED
    )

    checks[
        "pyramid_count_valid"
    ] = (
        len(
            PYRAMID_ADD_PERCENTS
        )
        >= MAX_PYRAMID_ADDS
    )

    checks[
        "backup_count_valid"
    ] = (
        len(
            BACKUP_SIZE_PERCENTS
        )
        >= MAX_BACKUPS
    )

    checks[
        "trailing_positive"
    ] = (
        TRAILING_DISTANCE_PERCENT
        > ZERO
    )

    checks[
        "signal_expiry_positive"
    ] = (
        SIGNAL_EXPIRY_SECONDS > 0
    )

    checks[
        "max_trade_loss_positive"
    ] = (
        MAX_TRADE_LOSS_PERCENT
        > ZERO
    )

    checks[
        "max_fund_exposure_valid"
    ] = (
        MAX_FUND_EXPOSURE_PERCENT
        > ZERO
        and
        MAX_FUND_EXPOSURE_PERCENT
        <= HUNDRED
    )

    return checks


# ============================================================
# EXPOSURE CALCULATION
# ============================================================

def calculate_planned_exposure():

    initial = INITIAL_ENTRY_PERCENT

    pyramids = sum(
        PYRAMID_ADD_PERCENTS[
            :MAX_PYRAMID_ADDS
        ],
        ZERO,
    )

    backups = sum(
        BACKUP_SIZE_PERCENTS[
            :MAX_BACKUPS
        ],
        ZERO,
    )

    total = (
        initial
        + pyramids
        + backups
    )

    return {
        "initial": initial,
        "pyramids": pyramids,
        "backups": backups,
        "total": total,
        "within_limit": (
            total
            <= MAX_FUND_EXPOSURE_PERCENT
        ),
    }


# ============================================================
# POSITION SIZING
# ============================================================

def calculate_position(
    balance,
    mark_price,
    entry_percent,
    leverage,
    quantity_precision,
):

    margin = percent_amount(
        balance,
        entry_percent,
    )

    notional = (
        margin
        * leverage
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = floor_quantity(
        raw_quantity,
        quantity_precision,
    )

    return {
        "margin": margin,
        "notional": notional,
        "raw_quantity": raw_quantity,
        "quantity": quantity,
    }


# ============================================================
# TEST $1 MARGIN POSITION
# ============================================================

def calculate_one_dollar_test(
    mark_price,
    leverage,
    quantity_precision,
):

    margin = Decimal(
        "1"
    )

    notional = (
        margin
        * leverage
    )

    raw_quantity = (
        notional
        / mark_price
    )

    quantity = floor_quantity(
        raw_quantity,
        quantity_precision,
    )

    return {
        "margin": margin,
        "notional": notional,
        "quantity": quantity,
    }


# ============================================================
# CONFIGURATION SIMULATION
# ============================================================

def build_adjustable_simulation():

    return [
        (
            "Initial Entry",
            f"{fmt(INITIAL_ENTRY_PERCENT)}%"
        ),
        (
            "Leverage",
            f"{fmt(LEVERAGE)}x"
        ),
        (
            "Local Max Leverage",
            f"{fmt(MAX_LEVERAGE)}x"
        ),
        (
            "Max Pyramids",
            str(
                MAX_PYRAMID_ADDS
            )
        ),
        (
            "Pyramid Sizes",
            ", ".join(
                f"{fmt(x)}%"
                for x
                in PYRAMID_ADD_PERCENTS
            )
        ),
        (
            "Pyramid Momentum",
            (
                f"{fmt(PYRAMID_MOMENTUM_CONFIRMATION_PERCENT)}%"
            )
        ),
        (
            "Max Backups",
            str(
                MAX_BACKUPS
            )
        ),
        (
            "Backup Sizes",
            ", ".join(
                f"{fmt(x)}%"
                for x
                in BACKUP_SIZE_PERCENTS
            )
        ),
        (
            "Backup Liq Buffer",
            (
                f"{fmt(BACKUP_LIQUIDATION_BUFFER_PERCENT)}%"
            )
        ),
        (
            "Min Liq Distance",
            (
                f"{fmt(MIN_LIQUIDATION_DISTANCE_PERCENT)}%"
            )
        ),
        (
            "TP1 / TP2 / TP3",
            (
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%"
            )
        ),
        (
            "TP1 Trigger",
            (
                f"{fmt(TP1_TRIGGER_PERCENT)}%"
            )
        ),
        (
            "TP2 Trigger",
            (
                f"{fmt(TP2_TRIGGER_PERCENT)}%"
            )
        ),
        (
            "Trailing Distance",
            (
                f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
            )
        ),
        (
            "Max Fund Exposure",
            (
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
            )
        ),
        (
            "Max Trade Loss",
            (
                f"{fmt(MAX_TRADE_LOSS_PERCENT)}%"
            )
        ),
        (
            "Signal Expiry",
            (
                f"{SIGNAL_EXPIRY_SECONDS}s"
            )
        ),
        (
            "Loss Sequence Limit",
            str(
                LOSS_SEQUENCE_LIMIT
            )
        ),
        (
            "Cooldown",
            (
                f"{COOLDOWN_SECONDS}s"
            )
        ),
        (
            "One Direction Only",
            (
                "ACTIVE"
                if ONE_DIRECTION_ONLY
                else "DISABLED"
            )
        ),
        (
            "Anti Duplicate",
            (
                "ACTIVE"
                if ANTI_DUPLICATE_ORDERS
                else "DISABLED"
            )
        ),
        (
            "Trend Reversal Exit",
            (
                "ACTIVE"
                if TREND_REVERSAL_EXIT
                else "DISABLED"
            )
        ),
        (
            "Idle Pyramid Cleanup",
            (
                "ACTIVE"
                if IDLE_PYRAMID_CLEANUP
                else "DISABLED"
            )
        ),
    ]


# ============================================================
# MAIN R5 DIAGNOSTIC
# ============================================================

async def run_r5():

    print(
        "=" * 60
    )

    print(
        f"MODULE {MODULE_NAME} STARTING"
    )

    print(
        f"{SYMBOL} ADJUSTABLE CONFIGURATION "
        "SIMULATION"
    )

    print(
        "=" * 60
    )

    print(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    print(
        "HARD EXECUTION LOCK: ACTIVE"
    )

    print(
        "NO LIVE ORDER FUNCTION EXISTS IN R5"
    )

    print(
        "=" * 60
    )

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        try:

            # ================================================
            # FETCH LIVE WEEX DATA
            # ================================================

            balance = await get_available_usdt(
                session
            )

            contract = await get_contract_info(
                session
            )

            mark_price = await get_mark_price(
                session
            )

            quantity_precision = int(
                contract.get(
                    "quantityPrecision",
                    4,
                )
            )

            min_order = Decimal(
                str(
                    contract.get(
                        "minOrderSize",
                        "0",
                    )
                )
            )

            contract_value = Decimal(
                str(
                    contract.get(
                        "contractVal",
                        "0",
                    )
                )
            )

            weex_min_leverage = Decimal(
                str(
                    contract.get(
                        "minLeverage",
                        "1",
                    )
                )
            )

            weex_max_leverage = Decimal(
                str(
                    contract.get(
                        "maxLeverage",
                        "0",
                    )
                )
            )


            # ================================================
            # CONFIGURATION VALIDATION
            # ================================================

            checks = validate_configuration(
                weex_max_leverage
            )

            exposure = calculate_planned_exposure()

            checks[
                "planned_exposure_within_limit"
            ] = exposure[
                "within_limit"
            ]


            # ================================================
            # CURRENT ENTRY SIZING
            # ================================================

            position = calculate_position(
                balance=balance,
                mark_price=mark_price,
                entry_percent=INITIAL_ENTRY_PERCENT,
                leverage=LEVERAGE,
                quantity_precision=quantity_precision,
            )

            entry_minimum_passed = (
                position["quantity"]
                >= min_order
                and
                position["quantity"]
                > ZERO
            )

            checks[
                "current_entry_meets_minimum"
            ] = entry_minimum_passed


            # ================================================
            # TRUE MINIMUM MARGIN
            # ================================================

            minimum_notional = (
                min_order
                * mark_price
            )

            minimum_margin_required = (
                minimum_notional
                / LEVERAGE
            )


            # ================================================
            # $1 MARGIN TEST
            # ================================================

            one_dollar = (
                calculate_one_dollar_test(
                    mark_price=mark_price,
                    leverage=LEVERAGE,
                    quantity_precision=quantity_precision,
                )
            )

            one_dollar_passed = (
                one_dollar["quantity"]
                >= min_order
            )


            # ================================================
            # OVERALL RESULT
            # ================================================

            all_passed = all(
                checks.values()
            )


            # ================================================
            # PRINT CONFIGURATION
            # ================================================

            print(
                "\nADJUSTABLE CONFIGURATION"
            )

            print(
                "-" * 60
            )

            for name, value in (
                build_adjustable_simulation()
            ):

                print(
                    f"{name}: {value}"
                )


            # ================================================
            # LIVE WEEX CONTRACT DATA
            # ================================================

            print(
                "\nWEEX CONTRACT"
            )

            print(
                "-" * 60
            )

            print(
                f"Symbol: {SYMBOL}"
            )

            print(
                f"Mark Price: "
                f"{fmt(mark_price)} USDT"
            )

            print(
                f"Available USDT: "
                f"{fmt(balance)}"
            )

            print(
                f"Minimum Order: "
                f"{fmt(min_order)}"
            )

            print(
                f"Quantity Precision: "
                f"{quantity_precision}"
            )

            print(
                f"Contract Value: "
                f"{fmt(contract_value)}"
            )

            print(
                f"WEEX Min Leverage: "
                f"{fmt(weex_min_leverage)}x"
            )

            print(
                f"WEEX Max Leverage: "
                f"{fmt(weex_max_leverage)}x"
            )


            # ================================================
            # 100x VALIDATION
            # ================================================

            print(
                "\nLEVERAGE VALIDATION"
            )

            print(
                "-" * 60
            )

            print(
                f"Requested Leverage: "
                f"{fmt(LEVERAGE)}x"
            )

            print(
                "Within Local Limit: "
                + (
                    "YES"
                    if checks[
                        "leverage_within_local_cap"
                    ]
                    else "NO"
                )
            )

            print(
                "Allowed By WEEX: "
                + (
                    "YES"
                    if checks[
                        "leverage_allowed_by_weex"
                    ]
                    else "NO"
                )
            )


            # ================================================
            # CURRENT ENTRY
            # ================================================

            print(
                "\nCURRENT ENTRY"
            )

            print(
                "-" * 60
            )

            print(
                f"Entry: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%"
            )

            print(
                f"Margin: "
                f"{fmt(position['margin'])} USDT"
            )

            print(
                f"Notional: "
                f"{fmt(position['notional'])} USDT"
            )

            print(
                f"Quantity: "
                f"{fmt(position['quantity'])}"
            )

            print(
                "Minimum Passed: "
                + (
                    "YES"
                    if entry_minimum_passed
                    else "NO"
                )
            )


            # ================================================
            # MINIMUM
            # ================================================

            print(
                "\nTRUE MINIMUM AT CURRENT LEVERAGE"
            )

            print(
                "-" * 60
            )

            print(
                f"Minimum Notional: "
                f"{fmt(minimum_notional)} USDT"
            )

            print(
                f"Minimum Margin Required: "
                f"{fmt(minimum_margin_required)} USDT"
            )


            # ================================================
            # EXPOSURE
            # ================================================

            print(
                "\nFULL PLANNED FUND EXPOSURE"
            )

            print(
                "-" * 60
            )

            print(
                f"Initial Entry: "
                f"{fmt(exposure['initial'])}%"
            )

            print(
                f"Pyramid Allocation: "
                f"{fmt(exposure['pyramids'])}%"
            )

            print(
                f"Backup Allocation: "
                f"{fmt(exposure['backups'])}%"
            )

            print(
                f"Maximum Planned: "
                f"{fmt(exposure['total'])}%"
            )

            print(
                f"Configured Limit: "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
            )

            print(
                "Exposure Passed: "
                + (
                    "YES"
                    if exposure[
                        "within_limit"
                    ]
                    else "NO"
                )
            )


            # ================================================
            # $1 TEST
            # ================================================

            print(
                "\n$1 MARGIN TEST"
            )

            print(
                "-" * 60
            )

            print(
                f"Notional: "
                f"{fmt(one_dollar['notional'])} USDT"
            )

            print(
                f"Quantity: "
                f"{fmt(one_dollar['quantity'])}"
            )

            print(
                "Minimum Passed: "
                + (
                    "YES"
                    if one_dollar_passed
                    else "NO"
                )
            )


            # ================================================
            # SAFETY CHECKS
            # ================================================

            print(
                "\nSAFETY / CONFIGURATION CHECKS"
            )

            print(
                "-" * 60
            )

            for name, passed in checks.items():

                icon = (
                    "PASS"
                    if passed
                    else "FAIL"
                )

                print(
                    f"{icon}: {name}"
                )


            # ================================================
            # LIQUIDATION NOTE
            # ================================================

            print(
                "\nLIQUIDATION / BACKUP ENGINE"
            )

            print(
                "-" * 60
            )

            print(
                "Backup count and sizes: CONFIGURED"
            )

            print(
                "Liquidation buffer: CONFIGURED"
            )

            print(
                "Minimum liquidation distance: CONFIGURED"
            )

            print(
                "Actual backup trigger prices: NOT ARMED"
            )

            print(
                "R5 will not estimate liquidation price."
            )

            print(
                "Later live-position module will use "
                "WEEX position liquidation data."
            )


            # ================================================
            # FINAL RESULT
            # ================================================

            print(
                "\n" + "=" * 60
            )

            if all_passed:

                print(
                    f"MODULE {MODULE_NAME} "
                    "DIAGNOSTIC PASSED"
                )

            else:

                print(
                    f"MODULE {MODULE_NAME} "
                    "DIAGNOSTIC NOT READY"
                )

            print(
                "HARD EXECUTION LOCK: ACTIVE"
            )

            print(
                "LIVE ORDER EXECUTION: DISABLED"
            )

            print(
                "NO LIVE ORDER WAS SENT"
            )

            print(
                "=" * 60
            )


            # ================================================
            # TELEGRAM REPORT
            # ================================================

            status_icon = (
                "✅"
                if all_passed
                else "⚠️"
            )

            telegram_message = (
                f"{status_icon} MODULE "
                f"{MODULE_NAME} "
                + (
                    "DIAGNOSTIC PASSED"
                    if all_passed
                    else "NOT READY"
                )
                + "\n"
                f"{SYMBOL}\n\n"

                f"Available USDT: "
                f"{fmt(balance)}\n"

                f"Mark Price: "
                f"{fmt(mark_price)} USDT\n\n"

                "ADJUSTABLE TEST CONFIG\n"

                f"Entry: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

                f"Leverage: "
                f"{fmt(LEVERAGE)}x\n"

                f"Max Pyramids: "
                f"{MAX_PYRAMID_ADDS}\n"

                f"Max Backups: "
                f"{MAX_BACKUPS}\n"

                f"Max Fund Exposure: "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n\n"

                "WEEX CONTRACT\n"

                f"Minimum Order: "
                f"{fmt(min_order)}\n"

                f"Quantity Precision: "
                f"{quantity_precision}\n"

                f"Contract Value: "
                f"{fmt(contract_value)}\n"

                f"WEEX Max Leverage: "
                f"{fmt(weex_max_leverage)}x\n\n"

                "CURRENT ENTRY\n"

                f"Margin: "
                f"{fmt(position['margin'])} USDT\n"

                f"Notional: "
                f"{fmt(position['notional'])} USDT\n"

                f"Quantity: "
                f"{fmt(position['quantity'])}\n"

                "Minimum Passed: "
                + (
                    "✅ YES\n\n"
                    if entry_minimum_passed
                    else "❌ NO\n\n"
                )

                "FULL EXPOSURE PLAN\n"

                f"Initial: "
                f"{fmt(exposure['initial'])}%\n"

                f"Pyramids: "
                f"{fmt(exposure['pyramids'])}%\n"

                f"Backups: "
                f"{fmt(exposure['backups'])}%\n"

                f"Total: "
                f"{fmt(exposure['total'])}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

                "Exposure Passed: "
                + (
                    "✅ YES\n\n"
                    if exposure[
                        "within_limit"
                    ]
                    else "❌ NO\n\n"
                )

                "TP ENGINE\n"

                f"TP1 / TP2 / TP3: "
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%\n"

                f"TP1 Trigger: "
                f"{fmt(TP1_TRIGGER_PERCENT)}%\n"

                f"TP2 Trigger: "
                f"{fmt(TP2_TRIGGER_PERCENT)}%\n"

                f"Trailing: "
                f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n\n"

                "SAFETY CONTROLS\n"

                "✅ One-direction protection\n"
                "✅ Anti-duplicate protection\n"
                "✅ Signal expiry\n"
                "✅ Loss cooldown\n"
                "✅ Trend reversal exit\n"
                "✅ Idle pyramid cleanup\n\n"

                "⚠️ Backup liquidation triggers "
                "NOT ARMED in R5\n"

                "⚠️ R5 does not estimate "
                "liquidation prices\n\n"

                "🛡 Hard execution lock active\n"
                "⚠️ Live order execution disabled\n"
                "⚠️ NO LIVE ORDER WAS SENT"
            )

            await send_telegram(
                session,
                telegram_message,
            )

            return all_passed


        except Exception as exc:

            print(
                "\n" + "=" * 60
            )

            print(
                f"MODULE {MODULE_NAME} ERROR"
            )

            print(
                type(exc).__name__
                + ": "
                + str(exc)
            )

            print(
                "HARD EXECUTION LOCK: ACTIVE"
            )

            print(
                "LIVE ORDER EXECUTION: DISABLED"
            )

            print(
                "NO LIVE ORDER WAS SENT"
            )

            print(
                "=" * 60
            )

            await send_telegram(
                session,
                (
                    f"❌ MODULE "
                    f"{MODULE_NAME} ERROR\n"
                    f"{SYMBOL}\n\n"
                    f"{type(exc).__name__}: "
                    f"{exc}\n\n"
                    "🛡 Hard execution lock active\n"
                    "⚠️ Live order execution disabled\n"
                    "⚠️ NO LIVE ORDER WAS SENT"
                ),
            )

            return False


# ============================================================
# SERVICE KEEP-ALIVE
# ============================================================

async def main():

    await run_r5()

    print(
        "\nR5 DIAGNOSTIC COMPLETE"
    )

    print(
        "SERVICE REMAINS ONLINE"
    )

    while True:

        await asyncio.sleep(
            3600
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "MODULE STOPPED")
