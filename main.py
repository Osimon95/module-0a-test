import asyncio
import base64
import hashlib
import hmac
import json
import os
import time

from decimal import Decimal, InvalidOperation, ROUND_DOWN
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
# ENVIRONMENT HELPERS
# ============================================================

def env_decimal(name, default):

    raw = os.getenv(
        name,
        default,
    ).strip()

    try:
        return Decimal(raw)

    except InvalidOperation as exc:
        raise RuntimeError(
            f"Invalid decimal environment variable "
            f"{name}={raw!r}"
        ) from exc


def env_int(name, default):

    raw = os.getenv(
        name,
        default,
    ).strip()

    try:
        return int(raw)

    except ValueError as exc:
        raise RuntimeError(
            f"Invalid integer environment variable "
            f"{name}={raw!r}"
        ) from exc


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


# ============================================================
# BTCUSDT CONFIRMED TEST BASELINE
# ============================================================

INITIAL_ENTRY_PERCENT = env_decimal(
    "INITIAL_ENTRY_PERCENT",
    "5",
)

LEVERAGE = env_decimal(
    "LEVERAGE",
    "100",
)

MAX_LEVERAGE = env_decimal(
    "MAX_LEVERAGE",
    "100",
)


# ============================================================
# PYRAMID CONFIGURATION
# ============================================================

MAX_PYRAMID_ADDS = env_int(
    "MAX_PYRAMID_ADDS",
    "1",
)

PYRAMID_ADD_PERCENTS_TEXT = os.getenv(
    "PYRAMID_ADD_PERCENTS",
    "5",
).strip()

PYRAMID_MOMENTUM_CONFIRMATION_PERCENT = env_decimal(
    "PYRAMID_MOMENTUM_CONFIRMATION_PERCENT",
    "0.30",
)


# ============================================================
# BACKUP CONFIGURATION
# ============================================================

MAX_BACKUPS = env_int(
    "MAX_BACKUPS",
    "3",
)

BACKUP_SIZE_PERCENTS_TEXT = os.getenv(
    "BACKUP_SIZE_PERCENTS",
    "5,5,5",
).strip()

BACKUP_LIQUIDATION_BUFFER_PERCENT = env_decimal(
    "BACKUP_LIQUIDATION_BUFFER_PERCENT",
    "1.00",
)

MIN_LIQUIDATION_DISTANCE_PERCENT = env_decimal(
    "MIN_LIQUIDATION_DISTANCE_PERCENT",
    "2.00",
)


# ============================================================
# TAKE PROFIT CONFIGURATION
# ============================================================

TP1_PERCENT = env_decimal(
    "TP1_PERCENT",
    "20",
)

TP2_PERCENT = env_decimal(
    "TP2_PERCENT",
    "20",
)

TP3_PERCENT = env_decimal(
    "TP3_PERCENT",
    "60",
)

TP1_TRIGGER_PERCENT = env_decimal(
    "TP1_TRIGGER_PERCENT",
    "0.50",
)

TP2_TRIGGER_PERCENT = env_decimal(
    "TP2_TRIGGER_PERCENT",
    "1.00",
)

TRAILING_DISTANCE_PERCENT = env_decimal(
    "TRAILING_DISTANCE_PERCENT",
    "0.20",
)


# ============================================================
# SAFETY / CONTROL CONFIGURATION
# ============================================================

MAX_FUND_EXPOSURE_PERCENT = env_decimal(
    "MAX_FUND_EXPOSURE_PERCENT",
    "35",
)

MAX_TRADE_LOSS_PERCENT = env_decimal(
    "MAX_TRADE_LOSS_PERCENT",
    "5",
)

SIGNAL_EXPIRY_SECONDS = env_int(
    "SIGNAL_EXPIRY_SECONDS",
    "180",
)

LOSS_SEQUENCE_LIMIT = env_int(
    "LOSS_SEQUENCE_LIMIT",
    "2",
)

COOLDOWN_SECONDS = env_int(
    "COOLDOWN_SECONDS",
    "900",
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
# These are deliberately hardcoded.
#
# Render environment variables CANNOT enable live trading.
#
# There is NO live order submission function in this R5.
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
HUNDRED = Decimal("100")


def D(value):
    return Decimal(str(value))


def fmt(value):

    if not isinstance(
        value,
        Decimal,
    ):
        value = D(value)

    text = format(
        value.normalize(),
        "f",
    )

    if "." in text:
        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text or "0"


def percent_amount(
    balance,
    percent,
):

    return (
        balance
        * percent
        / HUNDRED
    )


def parse_decimal_list(
    text,
    name,
):

    if not text:
        return []

    result = []

    for item in text.split(","):

        item = item.strip()

        if not item:
            continue

        try:
            result.append(
                Decimal(item)
            )

        except InvalidOperation as exc:
            raise RuntimeError(
                f"Invalid decimal in "
                f"{name}: {item!r}"
            ) from exc

    return result


PYRAMID_ADD_PERCENTS = parse_decimal_list(
    PYRAMID_ADD_PERCENTS_TEXT,
    "PYRAMID_ADD_PERCENTS",
)

BACKUP_SIZE_PERCENTS = parse_decimal_list(
    BACKUP_SIZE_PERCENTS_TEXT,
    "BACKUP_SIZE_PERCENTS",
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

    message = (
        timestamp
        + method.upper()
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
            time.time()
            * 1000
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

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Invalid JSON received "
                "from WEEX private API."
            ) from exc


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
        url
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

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Invalid JSON received "
                "from WEEX public API."
            ) from exc


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

        return False

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

            text = await response.text()

            if response.status == 200:

                print(
                    "TELEGRAM MESSAGE SENT"
                )

                return True

            print(
                "TELEGRAM ERROR:",
                response.status,
                text,
            )

            return False

    except Exception as exc:

        print(
            "TELEGRAM ERROR:",
            repr(exc),
        )

        return False


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

    if isinstance(
        data,
        dict,
    ):

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

    if isinstance(
        data,
        dict,
    ):

        symbols = data.get(
            "symbols",
            [],
        )

        if not symbols:

            nested = data.get(
                "data",
                {},
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

    if isinstance(
        data,
        dict,
    ):

        if "price" in data:

            return Decimal(
                str(
                    data["price"]
                )
            )

        nested = data.get(
            "data"
        )

        if (
            isinstance(
                nested,
                dict,
            )
            and
            "price" in nested
        ):

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
    weex_min_leverage,
    weex_max_leverage,
):

    checks = {}

    checks[
        "entry_positive"
    ] = (
        INITIAL_ENTRY_PERCENT
        > ZERO
    )

    checks[
        "entry_not_over_100"
    ] = (
        INITIAL_ENTRY_PERCENT
        <= HUNDRED
    )

    checks[
        "leverage_positive"
    ] = (
        LEVERAGE
        > ZERO
    )

    checks[
        "leverage_within_local_cap"
    ] = (
        LEVERAGE
        <= MAX_LEVERAGE
    )

    checks[
        "leverage_above_weex_min"
    ] = (
        LEVERAGE
        >= weex_min_leverage
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
        "tp_values_nonnegative"
    ] = (
        TP1_PERCENT >= ZERO
        and
        TP2_PERCENT >= ZERO
        and
        TP3_PERCENT >= ZERO
    )

    checks[
        "tp_triggers_positive"
    ] = (
        TP1_TRIGGER_PERCENT > ZERO
        and
        TP2_TRIGGER_PERCENT > ZERO
    )

    checks[
        "tp2_trigger_above_tp1"
    ] = (
        TP2_TRIGGER_PERCENT
        > TP1_TRIGGER_PERCENT
    )

    checks[
        "pyramid_count_nonnegative"
    ] = (
        MAX_PYRAMID_ADDS >= 0
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
        "pyramid_sizes_positive"
    ] = all(
        x > ZERO
        for x
        in PYRAMID_ADD_PERCENTS[
            :MAX_PYRAMID_ADDS
        ]
    )

    checks[
        "backup_count_nonnegative"
    ] = (
        MAX_BACKUPS >= 0
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
        "backup_sizes_positive"
    ] = all(
        x > ZERO
        for x
        in BACKUP_SIZE_PERCENTS[
            :MAX_BACKUPS
        ]
    )

    checks[
        "backup_buffer_positive"
    ] = (
        BACKUP_LIQUIDATION_BUFFER_PERCENT
        > ZERO
    )

    checks[
        "min_liquidation_distance_positive"
    ] = (
        MIN_LIQUIDATION_DISTANCE_PERCENT
        > ZERO
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
        SIGNAL_EXPIRY_SECONDS
        > 0
    )

    checks[
        "loss_sequence_limit_positive"
    ] = (
        LOSS_SEQUENCE_LIMIT
        > 0
    )

    checks[
        "cooldown_nonnegative"
    ] = (
        COOLDOWN_SECONDS
        >= 0
    )

    checks[
        "max_trade_loss_valid"
    ] = (
        MAX_TRADE_LOSS_PERCENT
        > ZERO
        and
        MAX_TRADE_LOSS_PERCENT
        <= HUNDRED
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
# $1 MARGIN TEST
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
# DISPLAY HELPERS
# ============================================================

def list_percentages(
    values,
):

    return (
        ", ".join(
            f"{fmt(x)}%"
            for x
            in values
        )
        or "NONE"
    )


def control_status(
    enabled,
):

    return (
        "✅ ACTIVE"
        if enabled
        else "⚪ DISABLED"
    )


def build_adjustable_simulation():

    return [
        (
            "Initial Entry",
            f"{fmt(INITIAL_ENTRY_PERCENT)}%",
        ),
        (
            "Leverage",
            f"{fmt(LEVERAGE)}x",
        ),
        (
            "Local Max Leverage",
            f"{fmt(MAX_LEVERAGE)}x",
        ),
        (
            "Max Pyramids",
            str(
                MAX_PYRAMID_ADDS
            ),
        ),
        (
            "Pyramid Sizes",
            list_percentages(
                PYRAMID_ADD_PERCENTS
            ),
        ),
        (
            "Pyramid Momentum",
            (
                f"{fmt(PYRAMID_MOMENTUM_CONFIRMATION_PERCENT)}%"
            ),
        ),
        (
            "Max Backups",
            str(
                MAX_BACKUPS
            ),
        ),
        (
            "Backup Sizes",
            list_percentages(
                BACKUP_SIZE_PERCENTS
            ),
        ),
        (
            "Backup Liq Buffer",
            (
                f"{fmt(BACKUP_LIQUIDATION_BUFFER_PERCENT)}%"
            ),
        ),
        (
            "Min Liq Distance",
            (
                f"{fmt(MIN_LIQUIDATION_DISTANCE_PERCENT)}%"
            ),
        ),
        (
            "TP1 / TP2 / TP3",
            (
                f"{fmt(TP1_PERCENT)}% / "
                f"{fmt(TP2_PERCENT)}% / "
                f"{fmt(TP3_PERCENT)}%"
            ),
        ),
        (
            "TP1 Trigger",
            f"{fmt(TP1_TRIGGER_PERCENT)}%",
        ),
        (
            "TP2 Trigger",
            f"{fmt(TP2_TRIGGER_PERCENT)}%",
        ),
        (
            "Trailing Distance",
            (
                f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
            ),
        ),
        (
            "Max Fund Exposure",
            (
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
            ),
        ),
        (
            "Max Trade Loss",
            (
                f"{fmt(MAX_TRADE_LOSS_PERCENT)}%"
            ),
        ),
        (
            "Signal Expiry",
            f"{SIGNAL_EXPIRY_SECONDS}s",
        ),
        (
            "Loss Sequence Limit",
            str(
                LOSS_SEQUENCE_LIMIT
            ),
        ),
        (
            "Cooldown",
            f"{COOLDOWN_SECONDS}s",
        ),
        (
            "One Direction Only",
            (
                "ACTIVE"
                if ONE_DIRECTION_ONLY
                else "DISABLED"
            ),
        ),
        (
            "Anti Duplicate",
            (
                "ACTIVE"
                if ANTI_DUPLICATE_ORDERS
                else "DISABLED"
            ),
        ),
        (
            "Trend Reversal Exit",
            (
                "ACTIVE"
                if TREND_REVERSAL_EXIT
                else "DISABLED"
            ),
        ),
        (
            "Idle Pyramid Cleanup",
            (
                "ACTIVE"
                if IDLE_PYRAMID_CLEANUP
                else "DISABLED"
            ),
        ),
    ]


# ============================================================
# TELEGRAM REPORT BUILDER
# ============================================================
#
# IMPORTANT:
#
# Building the Telegram report as a list of lines avoids the
# f-string / concatenation SyntaxError that occurred previously.
#
# ============================================================

def build_telegram_message(
    all_passed,
    balance,
    mark_price,
    min_order,
    quantity_precision,
    contract_value,
    weex_max_leverage,
    position,
    entry_minimum_passed,
    exposure,
    one_dollar,
    one_dollar_passed,
    checks,
):

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

    failed_checks = [
        name
        for name, passed
        in checks.items()
        if not passed
    ]

    lines = [
        (
            f"{status_icon} MODULE "
            f"{MODULE_NAME} "
            f"{status_text}"
        ),
        SYMBOL,
        "",
        (
            f"Available USDT: "
            f"{fmt(balance)}"
        ),
        (
            f"Mark Price: "
            f"{fmt(mark_price)} USDT"
        ),
        "",
        "ADJUSTABLE TEST CONFIG",
        (
            f"Entry: "
            f"{fmt(INITIAL_ENTRY_PERCENT)}%"
        ),
        (
            f"Leverage: "
            f"{fmt(LEVERAGE)}x"
        ),
        (
            f"Max Pyramids: "
            f"{MAX_PYRAMID_ADDS}"
        ),
        (
            f"Max Backups: "
            f"{MAX_BACKUPS}"
        ),
        (
            f"Max Fund Exposure: "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),
        "",
        "WEEX CONTRACT",
        (
            f"Minimum Order: "
            f"{fmt(min_order)}"
        ),
        (
            f"Quantity Precision: "
            f"{quantity_precision}"
        ),
        (
            f"Contract Value: "
            f"{fmt(contract_value)}"
        ),
        (
            f"WEEX Max Leverage: "
            f"{fmt(weex_max_leverage)}x"
        ),
        "",
        "CURRENT ENTRY",
        (
            f"Margin: "
            f"{fmt(position['margin'])} USDT"
        ),
        (
            f"Notional: "
            f"{fmt(position['notional'])} USDT"
        ),
        (
            f"Quantity: "
            f"{fmt(position['quantity'])}"
        ),
        (
            "Minimum Passed: ✅ YES"
            if entry_minimum_passed
            else "Minimum Passed: ❌ NO"
        ),
        "",
        "$1 MARGIN TEST",
        (
            f"Notional: "
            f"{fmt(one_dollar['notional'])} USDT"
        ),
        (
            f"Quantity: "
            f"{fmt(one_dollar['quantity'])}"
        ),
        (
            "Minimum Passed: ✅ YES"
            if one_dollar_passed
            else "Minimum Passed: ❌ NO"
        ),
        "",
        "FULL EXPOSURE PLAN",
        (
            f"Initial: "
            f"{fmt(exposure['initial'])}%"
        ),
        (
            f"Pyramids: "
            f"{fmt(exposure['pyramids'])}%"
        ),
        (
            f"Backups: "
            f"{fmt(exposure['backups'])}%"
        ),
        (
            f"Total: "
            f"{fmt(exposure['total'])}% / "
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
        ),
        (
            "Exposure Passed: ✅ YES"
            if exposure[
                "within_limit"
            ]
            else "Exposure Passed: ❌ NO"
        ),
        "",
        "TP ENGINE",
        (
            f"TP1 / TP2 / TP3: "
            f"{fmt(TP1_PERCENT)}% / "
            f"{fmt(TP2_PERCENT)}% / "
            f"{fmt(TP3_PERCENT)}%"
        ),
        (
            f"TP1 Trigger: "
            f"{fmt(TP1_TRIGGER_PERCENT)}%"
        ),
        (
            f"TP2 Trigger: "
            f"{fmt(TP2_TRIGGER_PERCENT)}%"
        ),
        (
            f"Trailing: "
            f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
        ),
        "",
        "SAFETY CONTROLS",
        (
            "One-direction: "
            + control_status(
                ONE_DIRECTION_ONLY
            )
        ),
        (
            "Anti-duplicate: "
            + control_status(
                ANTI_DUPLICATE_ORDERS
            )
        ),
        (
            f"Signal expiry: ✅ "
            f"{SIGNAL_EXPIRY_SECONDS}s"
        ),
        (
            f"Loss cooldown: ✅ after "
            f"{LOSS_SEQUENCE_LIMIT} losses / "
            f"{COOLDOWN_SECONDS}s"
        ),
        (
            "Trend reversal exit: "
            + control_status(
                TREND_REVERSAL_EXIT
            )
        ),
        (
            "Idle pyramid cleanup: "
            + control_status(
                IDLE_PYRAMID_CLEANUP
            )
        ),
    ]

    if failed_checks:

        lines.extend(
            [
                "",
                "FAILED CHECKS",
            ]
        )

        lines.extend(
            f"❌ {name}"
            for name
            in failed_checks
        )

    lines.extend(
        [
            "",
            (
                "⚠️ Backup liquidation triggers "
                "NOT ARMED in R5"
            ),
            (
                "⚠️ R5 does not estimate "
                "liquidation prices"
            ),
            "",
            "🛡 Hard execution lock active",
            "⚠️ Live order execution disabled",
            "⚠️ NO LIVE ORDER WAS SENT",
        ]
    )

    return "\n".join(
        lines
    )


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
            # LIVE WEEX DATA
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


            # ================================================
            # BASIC LIVE DATA VALIDATION
            # ================================================

            if balance < ZERO:

                raise RuntimeError(
                    "Available USDT balance "
                    "is negative."
                )

            if mark_price <= ZERO:

                raise RuntimeError(
                    f"Invalid WEEX mark price: "
                    f"{mark_price}"
                )


            # ================================================
            # CONTRACT DATA
            # ================================================

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
            # CONTRACT SANITY CHECK
            # ================================================

            if quantity_precision < 0:

                raise RuntimeError(
                    "WEEX returned an invalid "
                    "quantity precision."
                )

            if min_order <= ZERO:

                raise RuntimeError(
                    f"WEEX returned invalid "
                    f"minimum order size: "
                    f"{min_order}"
                )

            if weex_max_leverage <= ZERO:

                raise RuntimeError(
                    f"WEEX returned invalid "
                    f"maximum leverage: "
                    f"{weex_max_leverage}"
                )


            # ================================================
            # PREVENT INVALID DIVISION
            # ================================================

            if LEVERAGE <= ZERO:

                raise RuntimeError(
                    "Configured LEVERAGE must "
                    "be greater than zero."
                )


            # ================================================
            # CONFIGURATION VALIDATION
            # ================================================

            checks = validate_configuration(
                weex_min_leverage,
                weex_max_leverage,
            )

            exposure = (
                calculate_planned_exposure()
            )

            checks[
                "planned_exposure_within_limit"
            ] = exposure[
                "within_limit"
            ]


            # ================================================
            # CURRENT ENTRY POSITION
            # ================================================

            position = calculate_position(
                balance=balance,
                mark_price=mark_price,
                entry_percent=INITIAL_ENTRY_PERCENT,
                leverage=LEVERAGE,
                quantity_precision=quantity_precision,
            )

            entry_minimum_passed = (
                position[
                    "quantity"
                ]
                >= min_order
                and
                position[
                    "quantity"
                ]
                > ZERO
            )

            checks[
                "current_entry_meets_minimum"
            ] = entry_minimum_passed


            # ================================================
            # TRUE MINIMUM
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
                one_dollar[
                    "quantity"
                ]
                >= min_order
                and
                one_dollar[
                    "quantity"
                ]
                > ZERO
            )


            # ================================================
            # OVERALL RESULT
            # ================================================

            all_passed = all(
                checks.values()
            )


            # ================================================
            # ADJUSTABLE CONFIGURATION
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
            # WEEX CONTRACT
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
            # LEVERAGE VALIDATION
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
                "Above WEEX Minimum: "
                + (
                    "YES"
                    if checks[
                        "leverage_above_weex_min"
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
            # TRUE MINIMUM
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
            # SAFETY / CONFIGURATION CHECKS
            # ================================================

            print(
                "\nSAFETY / CONFIGURATION CHECKS"
            )

            print(
                "-" * 60
            )

            for name, passed in (
                checks.items()
            ):

                print(
                    f"{'PASS' if passed else 'FAIL'}: "
                    f"{name}"
                )


            # ================================================
            # LIQUIDATION / BACKUP ENGINE
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

            telegram_message = (
                build_telegram_message(
                    all_passed=all_passed,
                    balance=balance,
                    mark_price=mark_price,
                    min_order=min_order,
                    quantity_precision=quantity_precision,
                    contract_value=contract_value,
                    weex_max_leverage=weex_max_leverage,
                    position=position,
                    entry_minimum_passed=entry_minimum_passed,
                    exposure=exposure,
                    one_dollar=one_dollar,
                    one_dollar_passed=one_dollar_passed,
                    checks=checks,
                )
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
                f"{type(exc).__name__}: "
                f"{exc}"
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

            error_message = "\n".join(
                [
                    (
                        f"❌ MODULE "
                        f"{MODULE_NAME} ERROR"
                    ),
                    SYMBOL,
                    "",
                    (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                    "",
                    "🛡 Hard execution lock active",
                    "⚠️ Live order execution disabled",
                    "⚠️ NO LIVE ORDER WAS SENT",
                ]
            )

            await send_telegram(
                session,
                error_message,
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
