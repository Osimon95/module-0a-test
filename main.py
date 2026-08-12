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

MODULE_NAME = "0F-4H-R6"

API_BASE_URL = "https://api-contract.weex.com"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()


# ============================================================
# ADJUSTABLE CONFIGURATION
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

PYRAMID_ADD_PERCENT = Decimal(
    os.getenv(
        "PYRAMID_ADD_PERCENT",
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
# LIQUIDATION / BACKUP CONFIG
# ============================================================

BACKUP_LIQUIDATION_BUFFER_PERCENT = Decimal(
    os.getenv(
        "BACKUP_LIQUIDATION_BUFFER_PERCENT",
        "0.30",
    )
)

MIN_LIQUIDATION_DISTANCE_PERCENT = Decimal(
    os.getenv(
        "MIN_LIQUIDATION_DISTANCE_PERCENT",
        "0.20",
    )
)

# Planning estimate only.
# Real WEEX liquidatePrice overrides this for actual positions.

ESTIMATED_MAINTENANCE_MARGIN_RATE = Decimal(
    os.getenv(
        "ESTIMATED_MAINTENANCE_MARGIN_RATE",
        "0.005",
    )
)


# ============================================================
# SAFETY CONFIGURATION
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "180",
    )
)

LOSS_COOLDOWN_AFTER = int(
    os.getenv(
        "LOSS_COOLDOWN_AFTER",
        "2",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "900",
    )
)

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# HARD SAFETY LOCKS
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
# DECIMAL CONSTANTS
# ============================================================

D = Decimal

ZERO = D("0")

HUNDRED = D("100")


# ============================================================
# HELPERS
# ============================================================

def fmt(
    value,
    places=10,
):
    if isinstance(
        value,
        Decimal,
    ):
        result = (
            f"{value:.{places}f}"
            .rstrip("0")
            .rstrip(".")
        )

        return result or "0"

    return str(value)


def floor_qty(
    value,
    precision,
):
    step = D("1").scaleb(
        -precision
    )

    return value.quantize(
        step,
        rounding=ROUND_DOWN,
    )


def percent_of(
    value,
    percent,
):
    return (
        value
        * percent
        / HUNDRED
    )


# ============================================================
# WEEX SIGNING
# ============================================================

def sign_request(
    timestamp,
    method,
    path,
    query="",
    body="",
):
    request_path = (
        path
        + (
            "?" + query
            if query
            else ""
        )
    )

    prehash = (
        f"{timestamp}"
        f"{method.upper()}"
        f"{request_path}"
        f"{body}"
    )

    digest = hmac.new(
        WEEX_API_SECRET.encode(),
        prehash.encode(),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(
        digest
    ).decode()


# ============================================================
# HTTP REQUESTS
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):
    async with session.get(
        API_BASE_URL + path,
        params=params,
        timeout=15,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text}"
            )

        return json.loads(
            text
        )


async def private_get(
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
            "WEEX credentials are missing"
        )

    params = params or {}

    query = urlencode(
        params
    )

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    headers = {
        "ACCESS-KEY":
            WEEX_API_KEY,

        "ACCESS-SIGN":
            sign_request(
                timestamp,
                "GET",
                path,
                query,
            ),

        "ACCESS-PASSPHRASE":
            WEEX_API_PASSPHRASE,

        "ACCESS-TIMESTAMP":
            timestamp,

        "Content-Type":
            "application/json",
    }

    url = (
        API_BASE_URL
        + path
        + (
            "?" + query
            if query
            else ""
        )
    )

    async with session.get(
        url,
        headers=headers,
        timeout=15,
    ) as response:

        text = await response.text()

        if response.status != 200:
            raise RuntimeError(
                f"WEEX PRIVATE HTTP "
                f"{response.status}: "
                f"{text}"
            )

        return json.loads(
            text
        )


# ============================================================
# TELEGRAM
# ============================================================

async def telegram(
    session,
    message,
):
    if not (
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM: credentials missing; "
            "message not sent"
        )

        return

    url = (
        "https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}"
        "/sendMessage"
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
            timeout=15,
        ) as response:

            text = await response.text()

            if response.status != 200:
                print(
                    f"TELEGRAM HTTP "
                    f"{response.status}: "
                    f"{text}"
                )
            else:
                print(
                    "TELEGRAM MESSAGE SENT"
                )

    except Exception as exc:
        print(
            "TELEGRAM ERROR: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )


# ============================================================
# EXCHANGE INFO
# ============================================================

def get_symbol_info(
    exchange_info,
):
    symbols = exchange_info.get(
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
        "in exchangeInfo"
    )


# ============================================================
# BALANCE
# ============================================================

def get_usdt_balance(
    balance_data,
):
    if isinstance(
        balance_data,
        list,
    ):
        rows = balance_data

    else:
        rows = balance_data.get(
            "data",
            balance_data,
        )

    if isinstance(
        rows,
        dict,
    ):
        rows = [
            rows
        ]

    for row in rows or []:

        if (
            str(
                row.get(
                    "asset",
                    "",
                )
            ).upper()
            == "USDT"
        ):
            return D(
                str(
                    row.get(
                        "availableBalance",
                        row.get(
                            "balance",
                            "0",
                        ),
                    )
                )
            )

    raise RuntimeError(
        "USDT balance not found"
    )


# ============================================================
# EXISTING POSITION
# ============================================================

def find_position(
    position_data,
):
    if isinstance(
        position_data,
        list,
    ):
        rows = position_data

    else:
        rows = position_data.get(
            "data",
            position_data,
        )

    if isinstance(
        rows,
        dict,
    ):
        rows = [
            rows
        ]

    for row in rows or []:

        symbol = str(
            row.get(
                "symbol",
                "",
            )
        ).upper()

        size = D(
            str(
                row.get(
                    "size",
                    "0",
                )
            )
        )

        if (
            symbol == SYMBOL
            and size > ZERO
        ):
            return row

    return None


# ============================================================
# LIQUIDATION ESTIMATOR
# ============================================================

def estimate_liquidation(
    entry,
    leverage,
    side,
):
    """
    Planning estimate only.

    Actual WEEX liquidatePrice,
    when supplied by WEEX for a real
    position, remains authoritative.
    """

    initial_margin_rate = (
        D("1")
        / leverage
    )

    maintenance_rate = (
        ESTIMATED_MAINTENANCE_MARGIN_RATE
    )

    if side == "LONG":

        factor = (
            D("1")
            - initial_margin_rate
            + maintenance_rate
        )

    else:

        factor = (
            D("1")
            + initial_margin_rate
            - maintenance_rate
        )

    return max(
        entry * factor,
        ZERO,
    )


# ============================================================
# BACKUP TRIGGER
# ============================================================

def backup_trigger(
    liquidation_price,
    side,
):
    buffer_ratio = (
        BACKUP_LIQUIDATION_BUFFER_PERCENT
        / HUNDRED
    )

    if side == "LONG":

        return (
            liquidation_price
            * (
                D("1")
                + buffer_ratio
            )
        )

    return (
        liquidation_price
        * (
            D("1")
            - buffer_ratio
        )
    )


# ============================================================
# LIQUIDATION DISTANCE
# ============================================================

def liquidation_distance(
    entry,
    liquidation_price,
):
    if entry <= ZERO:
        return ZERO

    return (
        abs(
            entry
            - liquidation_price
        )
        / entry
        * HUNDRED
    )


# ============================================================
# WEIGHTED AVERAGE
# ============================================================

def weighted_average(
    old_average,
    old_notional,
    add_price,
    add_notional,
):
    total_notional = (
        old_notional
        + add_notional
    )

    if total_notional <= ZERO:
        return old_average

    if old_average > ZERO:

        old_quantity = (
            old_notional
            / old_average
        )

    else:
        old_quantity = ZERO

    if add_price > ZERO:

        add_quantity = (
            add_notional
            / add_price
        )

    else:
        add_quantity = ZERO

    total_quantity = (
        old_quantity
        + add_quantity
    )

    if total_quantity <= ZERO:
        return old_average

    return (
        total_notional
        / total_quantity
    )


# ============================================================
# SIMULATED BACKUP ENGINE
# ============================================================

def simulate_side(
    balance,
    mark_price,
    side,
):
    initial_margin = percent_of(
        balance,
        INITIAL_ENTRY_PERCENT,
    )

    initial_notional = (
        initial_margin
        * LEVERAGE
    )

    average_price = mark_price

    total_notional = (
        initial_notional
    )

    exposure = (
        INITIAL_ENTRY_PERCENT
    )

    results = []

    liquidation_price = (
        estimate_liquidation(
            average_price,
            LEVERAGE,
            side,
        )
    )

    distance = (
        liquidation_distance(
            average_price,
            liquidation_price,
        )
    )

    results.append(
        (
            "INITIAL",
            average_price,
            liquidation_price,
            None,
            exposure,
            distance,
            True,
        )
    )

    for backup_number in range(
        1,
        MAX_BACKUPS + 1,
    ):

        trigger = (
            backup_trigger(
                liquidation_price,
                side,
            )
        )

        next_exposure = (
            exposure
            + BACKUP_SIZE_PERCENT
        )

        exposure_ok = (
            next_exposure
            <= MAX_FUND_EXPOSURE_PERCENT
        )

        distance_ok = (
            liquidation_distance(
                average_price,
                liquidation_price,
            )
            >=
            MIN_LIQUIDATION_DISTANCE_PERCENT
        )

        allowed = (
            exposure_ok
            and distance_ok
            and trigger > ZERO
        )

        if allowed:

            add_margin = (
                percent_of(
                    balance,
                    BACKUP_SIZE_PERCENT,
                )
            )

            add_notional = (
                add_margin
                * LEVERAGE
            )

            average_price = (
                weighted_average(
                    average_price,
                    total_notional,
                    trigger,
                    add_notional,
                )
            )

            total_notional += (
                add_notional
            )

            exposure = (
                next_exposure
            )

            liquidation_price = (
                estimate_liquidation(
                    average_price,
                    LEVERAGE,
                    side,
                )
            )

            distance = (
                liquidation_distance(
                    average_price,
                    liquidation_price,
                )
            )

        else:

            distance = (
                liquidation_distance(
                    average_price,
                    liquidation_price,
                )
            )

        results.append(
            (
                f"BACKUP {backup_number}",
                average_price,
                liquidation_price,
                trigger,
                exposure,
                distance,
                allowed,
            )
        )

        if not allowed:
            break

    return results


# ============================================================
# MAIN
# ============================================================

async def main():

    print(
        "=" * 60
    )

    print(
        f"MODULE {MODULE_NAME} STARTING"
    )

    print(
        f"{SYMBOL} "
        "LIQUIDATION + BACKUP DIAGNOSTIC"
    )

    print(
        "NO LIVE ORDERS WILL BE SENT"
    )

    print(
        "=" * 60
    )

    async with aiohttp.ClientSession() as session:

        try:

            (
                exchange_info,
                mark_data,
                balance_data,
                position_data,
            ) = await asyncio.gather(

                public_get(
                    session,
                    "/capi/v3/market/exchangeInfo",
                    {
                        "symbol":
                            SYMBOL
                    },
                ),

                public_get(
                    session,
                    "/capi/v3/market/symbolPrice",
                    {
                        "symbol":
                            SYMBOL,

                        "priceType":
                            "MARK",
                    },
                ),

                private_get(
                    session,
                    "/capi/v3/account/balance",
                ),

                private_get(
                    session,
                    "/capi/v3/account/position/singlePosition",
                    {
                        "symbol":
                            SYMBOL
                    },
                ),
            )


            # ================================================
            # CONTRACT DATA
            # ================================================

            info = get_symbol_info(
                exchange_info
            )

            balance = get_usdt_balance(
                balance_data
            )

            mark_price = D(
                str(
                    mark_data.get(
                        "price",
                        "0",
                    )
                )
            )

            quantity_precision = int(
                info.get(
                    "quantityPrecision",
                    4,
                )
            )

            minimum_order = D(
                str(
                    info.get(
                        "minOrderSize",
                        info.get(
                            "minOrderQty",
                            "0.0001",
                        ),
                    )
                )
            )

            contract_value = D(
                str(
                    info.get(
                        "contractVal",
                        "0.0001",
                    )
                )
            )

            weex_max_leverage = D(
                str(
                    info.get(
                        "maxLeverage",
                        "0",
                    )
                )
            )


            # ================================================
            # CURRENT ENTRY
            # ================================================

            entry_margin = (
                percent_of(
                    balance,
                    INITIAL_ENTRY_PERCENT,
                )
            )

            entry_notional = (
                entry_margin
                * LEVERAGE
            )

            if mark_price > ZERO:

                entry_quantity = (
                    floor_qty(
                        entry_notional
                        / mark_price,
                        quantity_precision,
                    )
                )

            else:

                entry_quantity = ZERO

            entry_minimum_ok = (
                entry_quantity
                >= minimum_order
                and entry_quantity > ZERO
            )


            # ================================================
            # EXPOSURE
            # ================================================

            planned_pyramids = (
                PYRAMID_ADD_PERCENT
                * D(
                    MAX_PYRAMID_ADDS
                )
            )

            planned_backups = (
                BACKUP_SIZE_PERCENT
                * D(
                    MAX_BACKUPS
                )
            )

            planned_total = (
                INITIAL_ENTRY_PERCENT
                + planned_pyramids
                + planned_backups
            )

            exposure_ok = (
                planned_total
                <= MAX_FUND_EXPOSURE_PERCENT
            )


            # ================================================
            # LEVERAGE CHECK
            # ================================================

            leverage_ok = (
                LEVERAGE
                <= weex_max_leverage
                and LEVERAGE
                <= MAX_LEVERAGE
            )


            # ================================================
            # TP CHECK
            # ================================================

            tp_ok = (
                TP1_PERCENT
                + TP2_PERCENT
                + TP3_PERCENT
                ==
                HUNDRED
            )


            # ================================================
            # REAL WEEX POSITION
            # ================================================

            position = find_position(
                position_data
            )

            real_liquidation = ZERO

            real_side = "NONE"

            real_average = ZERO

            if position:

                real_liquidation = D(
                    str(
                        position.get(
                            "liquidatePrice",
                            "0",
                        )
                    )
                )

                real_side = str(
                    position.get(
                        "side",
                        "",
                    )
                ).upper()

                real_size = D(
                    str(
                        position.get(
                            "size",
                            "0",
                        )
                    )
                )

                real_open_value = D(
                    str(
                        position.get(
                            "openValue",
                            "0",
                        )
                    )
                )

                if real_size > ZERO:

                    real_average = (
                        real_open_value
                        / real_size
                    )


            # ================================================
            # SIMULATED BACKUP PLANS
            # ================================================

            long_plan = simulate_side(
                balance,
                mark_price,
                "LONG",
            )

            short_plan = simulate_side(
                balance,
                mark_price,
                "SHORT",
            )


            backup_plan_ok = (
                all(
                    row[6]
                    for row
                    in long_plan[1:]
                )
                and
                all(
                    row[6]
                    for row
                    in short_plan[1:]
                )
            )


            # ================================================
            # MASTER CHECKS
            # ================================================

            checks = {

                "mark_price_positive":
                    mark_price > ZERO,

                "balance_positive":
                    balance > ZERO,

                "leverage_allowed":
                    leverage_ok,

                "entry_meets_minimum":
                    entry_minimum_ok,

                "exposure_within_limit":
                    exposure_ok,

                "tp_split_valid":
                    tp_ok,

                "backup_plan_valid":
                    backup_plan_ok,

                "hard_execution_lock":
                    HARD_EXECUTION_LOCK,

                "live_execution_disabled":
                    not LIVE_ORDER_EXECUTION,
            }


            all_passed = all(
                checks.values()
            )


            status_icon = (
                "✅"
                if all_passed
                else "⚠️"
            )


            # ================================================
            # TELEGRAM / LOG REPORT
            # ================================================

            lines = [

                (
                    f"{status_icon} MODULE "
                    f"{MODULE_NAME} "
                    +
                    (
                        "DIAGNOSTIC PASSED"
                        if all_passed
                        else "NOT READY"
                    )
                ),

                SYMBOL,

                "",

                (
                    "Available USDT: "
                    f"{fmt(balance)}"
                ),

                (
                    "Mark Price: "
                    f"{fmt(mark_price)} USDT"
                ),

                "",

                "ADJUSTABLE CONFIG",

                (
                    "Entry: "
                    f"{fmt(INITIAL_ENTRY_PERCENT)}%"
                ),

                (
                    "Leverage: "
                    f"{fmt(LEVERAGE)}x"
                ),

                (
                    "Max Pyramids: "
                    f"{MAX_PYRAMID_ADDS}"
                ),

                (
                    "Pyramid Size: "
                    f"{fmt(PYRAMID_ADD_PERCENT)}%"
                ),

                (
                    "Max Backups: "
                    f"{MAX_BACKUPS}"
                ),

                (
                    "Backup Size: "
                    f"{fmt(BACKUP_SIZE_PERCENT)}% each"
                ),

                (
                    "Max Fund Exposure: "
                    f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
                ),

                "",

                "WEEX CONTRACT",

                (
                    "Minimum Order: "
                    f"{fmt(minimum_order)}"
                ),

                (
                    "Quantity Precision: "
                    f"{quantity_precision}"
                ),

                (
                    "Contract Value: "
                    f"{fmt(contract_value)}"
                ),

                (
                    "WEEX Max Leverage: "
                    f"{fmt(weex_max_leverage)}x"
                ),

                "",

                "CURRENT ENTRY",

                (
                    "Margin: "
                    f"{fmt(entry_margin)} USDT"
                ),

                (
                    "Notional: "
                    f"{fmt(entry_notional)} USDT"
                ),

                (
                    "Quantity: "
                    f"{fmt(entry_quantity)}"
                ),

                (
                    "Minimum Passed: "
                    +
                    (
                        "✅ YES"
                        if entry_minimum_ok
                        else "❌ NO"
                    )
                ),

                "",

                "FULL EXPOSURE PLAN",

                (
                    "Initial: "
                    f"{fmt(INITIAL_ENTRY_PERCENT)}%"
                ),

                (
                    "Pyramids: "
                    f"{fmt(planned_pyramids)}%"
                ),

                (
                    "Backups: "
                    f"{fmt(planned_backups)}%"
                ),

                (
                    "Total: "
                    f"{fmt(planned_total)}% / "
                    f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%"
                ),

                (
                    "Exposure Passed: "
                    +
                    (
                        "✅ YES"
                        if exposure_ok
                        else "❌ NO"
                    )
                ),

                "",

                "LIQUIDATION SETTINGS",

                (
                    "Backup Buffer: "
                    f"{fmt(BACKUP_LIQUIDATION_BUFFER_PERCENT)}%"
                ),

                (
                    "Min Liq Distance: "
                    f"{fmt(MIN_LIQUIDATION_DISTANCE_PERCENT)}%"
                ),

                (
                    "Planning MMR: "
                    f"{fmt(ESTIMATED_MAINTENANCE_MARGIN_RATE * HUNDRED)}%"
                ),

                "",

                "REAL WEEX POSITION",
            ]


            # ================================================
            # REAL POSITION REPORT
            # ================================================

            if position:

                lines += [

                    (
                        "Side: "
                        f"{real_side}"
                    ),

                    (
                        "Approx Avg Entry: "
                        f"{fmt(real_average)}"
                    ),

                    (
                        "WEEX Liquidation Price: "
                        f"{fmt(real_liquidation)}"
                    ),

                    (
                        "✅ Live position liquidation "
                        "field read from WEEX"
                    ),
                ]

            else:

                lines += [

                    "No open position detected",

                    (
                        "WEEX Liquidation Price: "
                        "N/A"
                    ),
                ]


            # ================================================
            # PLAN FORMATTER
            # ================================================

            def append_plan(
                title,
                rows,
            ):

                lines.extend(
                    [
                        "",
                        title,
                    ]
                )

                for row in rows:

                    (
                        label,
                        average,
                        liquidation,
                        trigger,
                        exposure,
                        distance,
                        allowed,
                    ) = row

                    if label == "INITIAL":

                        lines.append(

                            "Initial Avg "
                            f"{fmt(average)}"
                            " | Est Liq "
                            f"{fmt(liquidation)}"
                            " | Distance "
                            f"{fmt(distance)}%"
                        )

                    else:

                        lines.append(

                            f"{label}: "
                            "Trigger "
                            f"{fmt(trigger)}"
                            " | New Avg "
                            f"{fmt(average)}"
                            " | New Est Liq "
                            f"{fmt(liquidation)}"
                            " | Exposure "
                            f"{fmt(exposure)}%"
                            " | "
                            +
                            (
                                "✅"
                                if allowed
                                else "❌"
                            )
                        )


            append_plan(
                "SIMULATED LONG BACKUP PLAN",
                long_plan,
            )

            append_plan(
                "SIMULATED SHORT BACKUP PLAN",
                short_plan,
            )


            # ================================================
            # REMAINING REPORT
            # ================================================

            lines += [

                "",

                "TP ENGINE",

                (
                    "TP1 / TP2 / TP3: "
                    f"{fmt(TP1_PERCENT)}% / "
                    f"{fmt(TP2_PERCENT)}% / "
                    f"{fmt(TP3_PERCENT)}%"
                ),

                (
                    "TP1 Trigger: "
                    f"{fmt(TP1_TRIGGER_PERCENT)}%"
                ),

                (
                    "TP2 Trigger: "
                    f"{fmt(TP2_TRIGGER_PERCENT)}%"
                ),

                (
                    "Trailing: "
                    f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
                ),

                "",

                "SAFETY CONTROLS",

                (
                    "One-direction: "
                    +
                    (
                        "✅ ACTIVE"
                        if ONE_DIRECTION_ONLY
                        else "❌ OFF"
                    )
                ),

                (
                    "Anti-duplicate: "
                    +
                    (
                        "✅ ACTIVE"
                        if ANTI_DUPLICATE_ORDERS
                        else "❌ OFF"
                    )
                ),

                (
                    "Signal expiry: ✅ "
                    f"{SIGNAL_EXPIRY_SECONDS}s"
                ),

                (
                    "Loss cooldown: ✅ after "
                    f"{LOSS_COOLDOWN_AFTER} losses / "
                    f"{LOSS_COOLDOWN_SECONDS}s"
                ),

                (
                    "Trend reversal exit: "
                    +
                    (
                        "✅ ACTIVE"
                        if TREND_REVERSAL_EXIT
                        else "❌ OFF"
                    )
                ),

                (
                    "Idle pyramid cleanup: "
                    +
                    (
                        "✅ ACTIVE"
                        if IDLE_PYRAMID_CLEANUP
                        else "❌ OFF"
                    )
                ),

                "",

                (
                    "⚠️ Simulated liquidation prices "
                    "are planning estimates only"
                ),

                (
                    "⚠️ WEEX liquidatePrice is "
                    "authoritative for real open positions"
                ),

                (
                    "⚠️ Backup orders are NOT armed "
                    "in R6"
                ),

                "🛡 Hard execution lock active",

                "⚠️ Live order execution disabled",

                "⚠️ NO LIVE ORDER WAS SENT",
            ]


            message = "\n".join(
                lines
            )


            # ================================================
            # CONSOLE
            # ================================================

            print(
                message
            )

            print(
                "=" * 60
            )


            # ================================================
            # TELEGRAM
            # ================================================

            await telegram(
                session,
                message,
            )


        except Exception as exc:

            message = (

                f"❌ MODULE {MODULE_NAME} ERROR\n"

                f"{SYMBOL}\n\n"

                f"{type(exc).__name__}: "
                f"{exc}\n\n"

                "🛡 Hard execution lock active\n"

                "⚠️ Live order execution disabled\n"

                "⚠️ NO LIVE ORDER WAS SENT"
            )

            print(
                message
            )

            await telegram(
                session,
                message,
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
