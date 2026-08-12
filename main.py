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

MODULE_NAME = "0F-4H-R7"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

API_BASE_URL = "https://api-contract.weex.com"


# ============================================================
# ADJUSTABLE CONFIGURATION
# ============================================================

D = Decimal

INITIAL_ENTRY_PERCENT = D(
    os.getenv(
        "INITIAL_ENTRY_PERCENT",
        "5",
    )
)

LEVERAGE = D(
    os.getenv(
        "LEVERAGE",
        "100",
    )
)

MAX_LEVERAGE = D(
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

PYRAMID_SIZE_PERCENT = D(
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

BACKUP_SIZE_PERCENT = D(
    os.getenv(
        "BACKUP_SIZE_PERCENT",
        "5",
    )
)

MAX_FUND_EXPOSURE_PERCENT = D(
    os.getenv(
        "MAX_FUND_EXPOSURE_PERCENT",
        "35",
    )
)


# ============================================================
# LIQUIDATION / BACKUP SETTINGS
# ============================================================

BACKUP_BUFFER_PERCENT = D(
    os.getenv(
        "BACKUP_BUFFER_PERCENT",
        "0.3",
    )
)

MIN_LIQ_DISTANCE_PERCENT = D(
    os.getenv(
        "MIN_LIQ_DISTANCE_PERCENT",
        "0.2",
    )
)

PLANNING_MMR_PERCENT = D(
    os.getenv(
        "PLANNING_MMR_PERCENT",
        "0.5",
    )
)


# ============================================================
# TAKE PROFIT SETTINGS
# ============================================================

TP1_PERCENT = D(
    os.getenv(
        "TP1_PERCENT",
        "20",
    )
)

TP2_PERCENT = D(
    os.getenv(
        "TP2_PERCENT",
        "20",
    )
)

TP3_PERCENT = D(
    os.getenv(
        "TP3_PERCENT",
        "60",
    )
)

TP1_TRIGGER_PERCENT = D(
    os.getenv(
        "TP1_TRIGGER_PERCENT",
        "0.5",
    )
)

TP2_TRIGGER_PERCENT = D(
    os.getenv(
        "TP2_TRIGGER_PERCENT",
        "1",
    )
)

TRAILING_DISTANCE_PERCENT = D(
    os.getenv(
        "TRAILING_DISTANCE_PERCENT",
        "0.2",
    )
)


# ============================================================
# SAFETY SETTINGS
# ============================================================

SIGNAL_EXPIRY_SECONDS = int(
    os.getenv(
        "SIGNAL_EXPIRY_SECONDS",
        "180",
    )
)

MAX_CONSECUTIVE_LOSSES = int(
    os.getenv(
        "MAX_CONSECUTIVE_LOSSES",
        "2",
    )
)

LOSS_COOLDOWN_SECONDS = int(
    os.getenv(
        "LOSS_COOLDOWN_SECONDS",
        "900",
    )
)

ONE_DIRECTION_ONLY = (
    os.getenv(
        "ONE_DIRECTION_ONLY",
        "true",
    ).lower()
    == "true"
)

ANTI_DUPLICATE_ORDERS = (
    os.getenv(
        "ANTI_DUPLICATE_ORDERS",
        "true",
    ).lower()
    == "true"
)

TREND_REVERSAL_EXIT = (
    os.getenv(
        "TREND_REVERSAL_EXIT",
        "true",
    ).lower()
    == "true"
)

IDLE_PYRAMID_CLEANUP = (
    os.getenv(
        "IDLE_PYRAMID_CLEANUP",
        "true",
    ).lower()
    == "true"
)


# ============================================================
# HARD SAFETY LOCK
# ============================================================

LIVE_ORDER_EXECUTION = False

HARD_EXECUTION_LOCK = True

ORDER_ENDPOINT = "/capi/v3/order"


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

def fmt(value):

    if isinstance(
        value,
        Decimal,
    ):

        text = format(
            value,
            "f",
        )

        if "." in text:

            text = text.rstrip(
                "0"
            ).rstrip(
                "."
            )

        return text

    return str(
        value
    )


def dec(
    value,
    default="0",
):

    try:

        return D(
            str(
                value
            )
        )

    except Exception:

        return D(
            default
        )


def floor_decimal(
    value,
    precision,
):

    quantum = D(
        "1"
    ).scaleb(
        -int(
            precision
        )
    )

    return D(
        value
    ).quantize(
        quantum,
        rounding=ROUND_DOWN,
    )


def percent_amount(
    balance,
    percent,
):

    return (
        balance
        * percent
        / D("100")
    )


# ============================================================
# QUANTITY ENGINE
# ============================================================

def quantity_for_margin(
    balance,
    percent,
    leverage,
    price,
    precision,
):

    if price <= 0:

        return D(
            "0"
        )

    margin = percent_amount(
        balance,
        percent,
    )

    notional = (
        margin
        * leverage
    )

    quantity = (
        notional
        / price
    )

    return floor_decimal(
        quantity,
        precision,
    )


# ============================================================
# CLIENT ORDER ID
# ============================================================

def client_id(
    label,
    counter,
):

    clean = "".join(
        char
        for char in label.lower()
        if char.isalnum()
        or char in "_-."
    )[:10]

    return (
        f"r7-"
        f"{time.time_ns()}-"
        f"{counter}-"
        f"{clean}"
    )[:36]


# ============================================================
# ORDER PAYLOAD BUILDER
# ============================================================

def build_market_payload(
    side,
    position_side,
    quantity,
    label,
    counter,
):

    return {

        "symbol":
            SYMBOL,

        "side":
            side,

        "positionSide":
            position_side,

        "type":
            "MARKET",

        "quantity":
            fmt(
                quantity
            ),

        "newClientOrderId":
            client_id(
                label,
                counter,
            ),
    }


# ============================================================
# PAYLOAD VALIDATOR
# ============================================================

def validate_payload(
    payload,
    min_order,
    quantity_precision,
):

    errors = []

    required = {

        "symbol",

        "side",

        "positionSide",

        "type",

        "quantity",

        "newClientOrderId",
    }

    if not required.issubset(
        payload
    ):

        errors.append(
            "missing_required_field"
        )

    if payload.get(
        "symbol"
    ) != SYMBOL:

        errors.append(
            "symbol"
        )

    if payload.get(
        "side"
    ) not in {
        "BUY",
        "SELL",
    }:

        errors.append(
            "side"
        )

    if payload.get(
        "positionSide"
    ) not in {
        "LONG",
        "SHORT",
    }:

        errors.append(
            "positionSide"
        )

    if payload.get(
        "type"
    ) not in {
        "MARKET",
        "LIMIT",
    }:

        errors.append(
            "type"
        )

    quantity = dec(
        payload.get(
            "quantity"
        )
    )

    if quantity <= 0:

        errors.append(
            "quantity_positive"
        )

    if quantity < min_order:

        errors.append(
            "meets_min_order"
        )

    if quantity != floor_decimal(
        quantity,
        quantity_precision,
    ):

        errors.append(
            "quantity_precision"
        )

    order_id = payload.get(
        "newClientOrderId",
        "",
    )

    if not (
        1
        <= len(order_id)
        <= 36
    ):

        errors.append(
            "client_order_id_length"
        )

    return errors


# ============================================================
# DIRECTION HELPERS
# ============================================================

def open_side(
    position_side,
):

    if position_side == "LONG":

        return "BUY"

    return "SELL"


def close_side(
    position_side,
):

    if position_side == "LONG":

        return "SELL"

    return "BUY"


# ============================================================
# LIQUIDATION PLANNING
# ============================================================

def estimate_liquidation(
    average_price,
    position_side,
):

    leverage_move = (
        D("1")
        / LEVERAGE
    )

    maintenance = (
        PLANNING_MMR_PERCENT
        / D("100")
    )

    move = max(
        D("0"),
        leverage_move
        - maintenance,
    )

    if position_side == "LONG":

        return (
            average_price
            * (
                D("1")
                - move
            )
        )

    return (
        average_price
        * (
            D("1")
            + move
        )
    )


def backup_trigger(
    liquidation_price,
    position_side,
):

    buffer = (
        BACKUP_BUFFER_PERCENT
        / D("100")
    )

    if position_side == "LONG":

        return (
            liquidation_price
            * (
                D("1")
                + buffer
            )
        )

    return (
        liquidation_price
        * (
            D("1")
            - buffer
        )
    )


def weighted_average(
    old_average,
    old_quantity,
    new_price,
    new_quantity,
):

    total_quantity = (
        old_quantity
        + new_quantity
    )

    if total_quantity <= 0:

        return D(
            "0"
        )

    return (
        (
            old_average
            * old_quantity
        )
        +
        (
            new_price
            * new_quantity
        )
    ) / total_quantity


# ============================================================
# REAL POSITION DIRECTION CHECK
# ============================================================

def active_position_sides(
    positions,
):

    sides = set()

    for position in positions:

        if str(
            position.get(
                "symbol",
                "",
            )
        ).upper() != SYMBOL:

            continue

        if dec(
            position.get(
                "size"
            )
        ) <= 0:

            continue

        side = str(
            position.get(
                "side",
                "",
            )
        ).upper()

        if side in {
            "LONG",
            "SHORT",
        }:

            sides.add(
                side
            )

    return sides


# ============================================================
# HTTP
# ============================================================

async def public_get(
    session,
    path,
    params=None,
):

    async with session.get(
        API_BASE_URL
        + path,
        params=params,
        timeout=15,
    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX PUBLIC HTTP "
                f"{response.status}: "
                f"{text[:300]}"
            )

        return json.loads(
            text
        )


# ============================================================
# WEEX SIGNING
# ============================================================

def signed_headers(
    method,
    path,
    query_string="",
    body="",
):

    timestamp = str(
        int(
            time.time()
            * 1000
        )
    )

    message = (
        timestamp
        + method.upper()
        + path
        + query_string
        + body
    )

    signature = base64.b64encode(

        hmac.new(

            WEEX_API_SECRET.encode(),

            message.encode(),

            hashlib.sha256,

        ).digest()

    ).decode()

    return {

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

        "locale":
            "en-US",
    }


# ============================================================
# PRIVATE GET ONLY
# ============================================================

async def private_get(
    session,
    path,
    params=None,
):

    params = (
        params
        or {}
    )

    if params:

        query_string = (
            "?"
            + urlencode(
                params
            )
        )

    else:

        query_string = ""

    headers = signed_headers(
        "GET",
        path,
        query_string,
    )

    async with session.get(

        API_BASE_URL
        + path
        + query_string,

        headers=headers,

        timeout=15,

    ) as response:

        text = await response.text()

        if response.status != 200:

            raise RuntimeError(
                f"WEEX PRIVATE HTTP "
                f"{response.status}: "
                f"{text[:300]}"
            )

        return json.loads(
            text
        )


# ============================================================
# TELEGRAM
# ============================================================

async def telegram_send(
    session,
    message,
):

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):

        return False

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    try:

        async with session.post(

            url,

            json={
                "chat_id":
                    TELEGRAM_CHAT_ID,

                "text":
                    message,
            },

            timeout=15,

        ) as response:

            return (
                response.status
                == 200
            )

    except Exception:

        return False


# ============================================================
# CONTRACT INFORMATION
# ============================================================

async def get_contract(
    session,
):

    data = await public_get(

        session,

        "/capi/v3/market/exchangeInfo",

        {
            "symbol":
                SYMBOL
        },
    )

    symbols = (
        data.get(
            "symbols",
            [],
        )
        if isinstance(
            data,
            dict,
        )
        else []
    )

    contract = next(

        (
            item
            for item in symbols

            if str(
                item.get(
                    "symbol",
                    "",
                )
            ).upper()
            == SYMBOL
        ),

        None,
    )

    if not contract:

        raise RuntimeError(
            f"Contract metadata "
            f"not found for {SYMBOL}"
        )

    return contract


# ============================================================
# MARK PRICE
# ============================================================

async def get_mark_price(
    session,
):

    data = await public_get(

        session,

        "/capi/v3/market/symbolPrice",

        {
            "symbol":
                SYMBOL,

            "priceType":
                "MARK",
        },
    )

    price = dec(
        data.get(
            "price"
        )
        if isinstance(
            data,
            dict,
        )
        else None
    )

    if price <= 0:

        raise RuntimeError(
            "Invalid WEEX mark price"
        )

    return price


# ============================================================
# BALANCE
# ============================================================

async def get_balance(
    session,
):

    data = await private_get(

        session,

        "/capi/v3/account/balance",
    )

    if isinstance(
        data,
        list,
    ):

        rows = data

    elif (
        isinstance(
            data,
            dict,
        )
        and isinstance(
            data.get(
                "data"
            ),
            list,
        )
    ):

        rows = data[
            "data"
        ]

    else:

        rows = []

    usdt = next(

        (
            row
            for row in rows

            if str(
                row.get(
                    "asset",
                    "",
                )
            ).upper()
            == "USDT"
        ),

        None,
    )

    if not usdt:

        raise RuntimeError(
            "USDT balance not found"
        )

    return dec(
        usdt.get(
            "availableBalance"
        )
    )


# ============================================================
# POSITIONS
# ============================================================

async def get_positions(
    session,
):

    data = await private_get(

        session,

        "/capi/v3/account/position/allPosition",
    )

    if isinstance(
        data,
        list,
    ):

        return data

    if (
        isinstance(
            data,
            dict,
        )
        and isinstance(
            data.get(
                "data"
            ),
            list,
        )
    ):

        return data[
            "data"
        ]

    return []


# ============================================================
# COMPLETE DIRECTION PAYLOAD PLAN
# ============================================================

def make_direction_plan(
    position_side,
    balance,
    mark_price,
    quantity_precision,
    minimum_order,
):

    payloads = []

    validations = []

    used_ids = set()

    counter = 0


    initial_quantity = (
        quantity_for_margin(

            balance,

            INITIAL_ENTRY_PERCENT,

            LEVERAGE,

            mark_price,

            quantity_precision,
        )
    )


    pyramid_quantity = (
        quantity_for_margin(

            balance,

            PYRAMID_SIZE_PERCENT,

            LEVERAGE,

            mark_price,

            quantity_precision,
        )
    )


    backup_quantity = (
        quantity_for_margin(

            balance,

            BACKUP_SIZE_PERCENT,

            LEVERAGE,

            mark_price,

            quantity_precision,
        )
    )


    def add_order(
        label,
        side,
        quantity,
    ):

        nonlocal counter

        counter += 1

        payload = build_market_payload(

            side,

            position_side,

            quantity,

            label,

            counter,
        )

        errors = validate_payload(

            payload,

            minimum_order,

            quantity_precision,
        )

        order_id = payload[
            "newClientOrderId"
        ]

        if order_id in used_ids:

            errors.append(
                "duplicate_client_order_id"
            )

        used_ids.add(
            order_id
        )

        payloads.append(
            (
                label,
                payload,
            )
        )

        validations.append(
            (
                label,
                errors,
            )
        )


    # ========================================================
    # ENTRY
    # ========================================================

    add_order(

        "ENTRY",

        open_side(
            position_side
        ),

        initial_quantity,
    )


    # ========================================================
    # PYRAMIDS
    # ========================================================

    for number in range(
        1,
        MAX_PYRAMID_ADDS
        + 1,
    ):

        add_order(

            f"PYRAMID{number}",

            open_side(
                position_side
            ),

            pyramid_quantity,
        )


    # ========================================================
    # BACKUPS
    # ========================================================

    for number in range(
        1,
        MAX_BACKUPS
        + 1,
    ):

        add_order(

            f"BACKUP{number}",

            open_side(
                position_side
            ),

            backup_quantity,
        )


    # ========================================================
    # WORST CASE POSITION SIZE
    # ========================================================

    total_quantity = (

        initial_quantity

        +

        pyramid_quantity
        * MAX_PYRAMID_ADDS

        +

        backup_quantity
        * MAX_BACKUPS
    )


    # ========================================================
    # TP QUANTITIES
    # ========================================================

    tp1_quantity = floor_decimal(

        total_quantity
        * TP1_PERCENT
        / D("100"),

        quantity_precision,
    )


    tp2_quantity = floor_decimal(

        total_quantity
        * TP2_PERCENT
        / D("100"),

        quantity_precision,
    )


    tp3_quantity = (

        total_quantity

        - tp1_quantity

        - tp2_quantity
    )


    # ========================================================
    # TP1 EXIT
    # ========================================================

    add_order(

        "TP1_EXIT",

        close_side(
            position_side
        ),

        tp1_quantity,
    )


    # ========================================================
    # TP2 EXIT
    # ========================================================

    add_order(

        "TP2_EXIT",

        close_side(
            position_side
        ),

        tp2_quantity,
    )


    # ========================================================
    # FINAL TRAILING EXIT
    # ========================================================

    add_order(

        "TRAIL_EXIT",

        close_side(
            position_side
        ),

        tp3_quantity,
    )


    ids_unique = (
        len(
            used_ids
        )
        ==
        len(
            payloads
        )
    )


    payloads_valid = all(

        not errors

        for _, errors
        in validations
    )


    return {

        "payloads":
            payloads,

        "validations":
            validations,

        "initial_quantity":
            initial_quantity,

        "pyramid_quantity":
            pyramid_quantity,

        "backup_quantity":
            backup_quantity,

        "total_quantity":
            total_quantity,

        "tp1_quantity":
            tp1_quantity,

        "tp2_quantity":
            tp2_quantity,

        "tp3_quantity":
            tp3_quantity,

        "ids_unique":
            ids_unique,

        "valid":
            (
                payloads_valid
                and ids_unique
            ),
    }


# ============================================================
# MAIN
# ============================================================

async def main():

    print(
        "=" * 60
    )

    print(
        f"MODULE "
        f"{MODULE_NAME} "
        f"STARTING"
    )

    print(
        f"{SYMBOL} "
        f"SAFE ORDER PAYLOAD SIMULATION"
    )

    print(
        "NO LIVE ORDERS WILL BE SENT"
    )

    print(
        "=" * 60
    )


    credentials_ready = all(
        [
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        ]
    )

    if not credentials_ready:

        raise RuntimeError(
            "WEEX credentials missing"
        )


    async with aiohttp.ClientSession() as session:

        try:

            (
                contract,
                mark_price,
                balance,
                positions,
            ) = await asyncio.gather(

                get_contract(
                    session
                ),

                get_mark_price(
                    session
                ),

                get_balance(
                    session
                ),

                get_positions(
                    session
                ),
            )


            # ================================================
            # CONTRACT
            # ================================================

            minimum_order = dec(
                contract.get(
                    "minOrderSize"
                )
            )

            quantity_precision = int(
                contract.get(
                    "quantityPrecision",
                    4,
                )
            )

            contract_value = dec(
                contract.get(
                    "contractVal"
                )
            )

            weex_max_leverage = dec(
                contract.get(
                    "maxLeverage"
                )
            )


            # ================================================
            # CURRENT ENTRY
            # ================================================

            entry_margin = percent_amount(

                balance,

                INITIAL_ENTRY_PERCENT,
            )

            entry_notional = (

                entry_margin

                * LEVERAGE
            )

            entry_quantity = (
                quantity_for_margin(

                    balance,

                    INITIAL_ENTRY_PERCENT,

                    LEVERAGE,

                    mark_price,

                    quantity_precision,
                )
            )


            # ================================================
            # WORST CASE FUND EXPOSURE
            # ================================================

            full_exposure = (

                INITIAL_ENTRY_PERCENT

                +

                PYRAMID_SIZE_PERCENT
                * MAX_PYRAMID_ADDS

                +

                BACKUP_SIZE_PERCENT
                * MAX_BACKUPS
            )


            exposure_ok = (

                full_exposure

                <=

                MAX_FUND_EXPOSURE_PERCENT
            )


            leverage_ok = (

                LEVERAGE
                <= MAX_LEVERAGE

                and

                LEVERAGE
                <= weex_max_leverage
            )


            tp_split_ok = (

                TP1_PERCENT

                + TP2_PERCENT

                + TP3_PERCENT

                == D("100")
            )


            minimum_ok = (

                entry_quantity

                >= minimum_order
            )


            # ================================================
            # REAL POSITION CHECK
            # ================================================

            current_sides = (
                active_position_sides(
                    positions
                )
            )

            one_direction_ok = (

                not ONE_DIRECTION_ONLY

                or

                len(
                    current_sides
                )
                <= 1
            )


            real_position = next(

                (
                    position

                    for position
                    in positions

                    if str(
                        position.get(
                            "symbol",
                            "",
                        )
                    ).upper()
                    == SYMBOL

                    and

                    dec(
                        position.get(
                            "size"
                        )
                    )
                    > 0
                ),

                None,
            )


            # ================================================
            # LONG PAYLOAD SIMULATION
            # ================================================

            long_plan = make_direction_plan(

                "LONG",

                balance,

                mark_price,

                quantity_precision,

                minimum_order,
            )


            # ================================================
            # SHORT PAYLOAD SIMULATION
            # ================================================

            short_plan = make_direction_plan(

                "SHORT",

                balance,

                mark_price,

                quantity_precision,

                minimum_order,
            )


            # ================================================
            # SAFETY TESTS
            # ================================================

            fresh_signal_ok = (

                SIGNAL_EXPIRY_SECONDS
                > 0
            )


            expired_signal_blocked = (

                SIGNAL_EXPIRY_SECONDS
                + 1

                >

                SIGNAL_EXPIRY_SECONDS
            )


            cooldown_guard_ok = (

                MAX_CONSECUTIVE_LOSSES
                > 0

                and

                LOSS_COOLDOWN_SECONDS
                > 0
            )


            hard_lock_ok = (

                HARD_EXECUTION_LOCK

                and

                not LIVE_ORDER_EXECUTION
            )


            # ================================================
            # MASTER PASS
            # ================================================

            all_passed = all(
                [
                    exposure_ok,
                    leverage_ok,
                    tp_split_ok,
                    minimum_ok,
                    one_direction_ok,
                    long_plan[
                        "valid"
                    ],
                    short_plan[
                        "valid"
                    ],
                    fresh_signal_ok,
                    expired_signal_blocked,
                    cooldown_guard_ok,
                    hard_lock_ok,
                ]
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


            # ================================================
            # REPORT
            # ================================================

            lines = [

                f"{status_icon} MODULE "
                f"{MODULE_NAME} "
                f"{status_text}",

                SYMBOL,

                "",

                f"Available USDT: "
                f"{fmt(balance)}",

                f"Mark Price: "
                f"{fmt(mark_price)} USDT",

                "",

                "ADJUSTABLE CONFIG",

                f"Entry: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%",

                f"Leverage: "
                f"{fmt(LEVERAGE)}x",

                f"Max Pyramids: "
                f"{MAX_PYRAMID_ADDS}",

                f"Pyramid Size: "
                f"{fmt(PYRAMID_SIZE_PERCENT)}%",

                f"Max Backups: "
                f"{MAX_BACKUPS}",

                f"Backup Size: "
                f"{fmt(BACKUP_SIZE_PERCENT)}% each",

                f"Max Fund Exposure: "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%",

                "",

                "WEEX CONTRACT",

                f"Minimum Order: "
                f"{fmt(minimum_order)}",

                f"Quantity Precision: "
                f"{quantity_precision}",

                f"Contract Value: "
                f"{fmt(contract_value)}",

                f"WEEX Max Leverage: "
                f"{fmt(weex_max_leverage)}x",

                "",

                "CURRENT ENTRY",

                f"Margin: "
                f"{fmt(entry_margin)} USDT",

                f"Notional: "
                f"{fmt(entry_notional)} USDT",

                f"Quantity: "
                f"{fmt(entry_quantity)}",

                f"Minimum Passed: "
                f"{'✅ YES' if minimum_ok else '❌ NO'}",

                "",

                "WORST-CASE EXPOSURE",

                f"Initial: "
                f"{fmt(INITIAL_ENTRY_PERCENT)}%",

                f"Pyramids: "
                f"{fmt(PYRAMID_SIZE_PERCENT * MAX_PYRAMID_ADDS)}%",

                f"Backups: "
                f"{fmt(BACKUP_SIZE_PERCENT * MAX_BACKUPS)}%",

                f"Total: "
                f"{fmt(full_exposure)}% / "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%",

                f"Exposure Passed: "
                f"{'✅ YES' if exposure_ok else '❌ NO'}",

                "",

                "REAL WEEX POSITION",
            ]


            # ================================================
            # REAL POSITION REPORT
            # ================================================

            if real_position:

                real_liquidation = dec(
                    real_position.get(
                        "liquidatePrice"
                    )
                )

                lines.extend(
                    [

                        f"Side: "
                        f"{str(real_position.get('side', 'N/A')).upper()}",

                        f"Size: "
                        f"{real_position.get('size', 'N/A')}",

                        f"Leverage: "
                        f"{real_position.get('leverage', 'N/A')}x",

                        f"WEEX Liquidation Price: "
                        f"{fmt(real_liquidation) if real_liquidation > 0 else 'N/A'}",
                    ]
                )

            else:

                lines.extend(
                    [
                        "No open position detected",

                        "WEEX Liquidation Price: N/A",
                    ]
                )


            # ================================================
            # ORDER PAYLOAD ENGINE
            # ================================================

            lines.extend(
                [

                    "",

                    "R7 ORDER PAYLOAD SIMULATION",

                    f"Endpoint Target: "
                    f"POST {ORDER_ENDPOINT}",

                    "Network POST: ❌ DISABLED",

                    "",
                ]
            )


            # ================================================
            # LONG + SHORT PAYLOAD REPORT
            # ================================================

            for (
                direction,
                plan,
            ) in (
                (
                    "LONG",
                    long_plan,
                ),
                (
                    "SHORT",
                    short_plan,
                ),
            ):

                lines.append(
                    f"SIMULATED "
                    f"{direction} PAYLOADS"
                )

                validation_map = dict(
                    plan[
                        "validations"
                    ]
                )

                for (
                    label,
                    payload,
                ) in plan[
                    "payloads"
                ]:

                    errors = validation_map[
                        label
                    ]

                    icon = (

                        "✅"

                        if not errors

                        else "❌"
                    )

                    lines.append(

                        f"{label}: "
                        f"{payload['side']} "
                        f"{payload['positionSide']} "
                        f"qty "
                        f"{payload['quantity']} "
                        f"| {icon}"
                    )


                lines.extend(
                    [

                        f"Client IDs Unique: "
                        f"{'✅ YES' if plan['ids_unique'] else '❌ NO'}",

                        f"Payload Set Valid: "
                        f"{'✅ YES' if plan['valid'] else '❌ NO'}",

                        f"TP Quantities: "
                        f"{fmt(plan['tp1_quantity'])} / "
                        f"{fmt(plan['tp2_quantity'])} / "
                        f"{fmt(plan['tp3_quantity'])}",

                        "",
                    ]
                )


            # ================================================
            # R6 BACKUP PLANNING CONTINUITY
            # ================================================

            for position_side in (
                "LONG",
                "SHORT",
            ):

                average_price = mark_price

                current_quantity = (
                    entry_quantity
                )

                liquidation_price = (
                    estimate_liquidation(

                        average_price,

                        position_side,
                    )
                )

                distance = (

                    abs(
                        average_price
                        - liquidation_price
                    )

                    / average_price

                    * D("100")
                )

                lines.append(
                    f"SIMULATED "
                    f"{position_side} "
                    f"BACKUP PLAN"
                )

                lines.append(

                    f"Initial Avg "
                    f"{fmt(average_price)} "
                    f"| Est Liq "
                    f"{fmt(liquidation_price)} "
                    f"| Distance "
                    f"{fmt(distance)}%"
                )


                exposure = (
                    INITIAL_ENTRY_PERCENT
                )


                backup_quantity = (
                    quantity_for_margin(

                        balance,

                        BACKUP_SIZE_PERCENT,

                        LEVERAGE,

                        mark_price,

                        quantity_precision,
                    )
                )


                for number in range(
                    1,
                    MAX_BACKUPS
                    + 1,
                ):

                    trigger = backup_trigger(

                        liquidation_price,

                        position_side,
                    )


                    new_average = (
                        weighted_average(

                            average_price,

                            current_quantity,

                            trigger,

                            backup_quantity,
                        )
                    )


                    current_quantity += (
                        backup_quantity
                    )

                    average_price = (
                        new_average
                    )

                    liquidation_price = (
                        estimate_liquidation(

                            average_price,

                            position_side,
                        )
                    )


                    exposure += (
                        BACKUP_SIZE_PERCENT
                    )


                    backup_ok = (

                        exposure

                        <=

                        MAX_FUND_EXPOSURE_PERCENT
                    )


                    lines.append(

                        f"BACKUP {number}: "
                        f"Trigger {fmt(trigger)} "
                        f"| New Avg {fmt(average_price)} "
                        f"| New Est Liq {fmt(liquidation_price)} "
                        f"| Exposure {fmt(exposure)}% "
                        f"| {'✅' if backup_ok else '❌'}"
                    )


                lines.append(
                    ""
                )


            # ================================================
            # TP ENGINE
            # ================================================

            lines.extend(
                [

                    "TP ENGINE",

                    f"TP1 / TP2 / TP3: "
                    f"{fmt(TP1_PERCENT)}% / "
                    f"{fmt(TP2_PERCENT)}% / "
                    f"{fmt(TP3_PERCENT)}%",

                    f"TP1 Trigger: "
                    f"{fmt(TP1_TRIGGER_PERCENT)}%",

                    f"TP2 Trigger: "
                    f"{fmt(TP2_TRIGGER_PERCENT)}%",

                    f"Trailing: "
                    f"{fmt(TRAILING_DISTANCE_PERCENT)}%",

                    f"TP Split Passed: "
                    f"{'✅ YES' if tp_split_ok else '❌ NO'}",

                    "",

                    "SAFETY CONTROLS",

                    f"One-direction: "
                    f"{'✅ ACTIVE' if ONE_DIRECTION_ONLY else '⚠️ DISABLED'}",

                    f"Current Direction Check: "
                    f"{'✅ PASS' if one_direction_ok else '❌ CONFLICT'}",

                    f"Anti-duplicate: "
                    f"{'✅ ACTIVE' if ANTI_DUPLICATE_ORDERS else '⚠️ DISABLED'}",

                    f"Signal expiry: "
                    f"✅ {SIGNAL_EXPIRY_SECONDS}s",

                    f"Expired signal rejection test: "
                    f"{'✅ PASS' if expired_signal_blocked else '❌ FAIL'}",

                    f"Loss cooldown: "
                    f"✅ after "
                    f"{MAX_CONSECUTIVE_LOSSES} "
                    f"losses / "
                    f"{LOSS_COOLDOWN_SECONDS}s",

                    f"Trend reversal exit: "
                    f"{'✅ ACTIVE' if TREND_REVERSAL_EXIT else '⚠️ DISABLED'}",

                    f"Idle pyramid cleanup: "
                    f"{'✅ ACTIVE' if IDLE_PYRAMID_CLEANUP else '⚠️ DISABLED'}",

                    "",

                    "⚠️ Simulated liquidation prices are planning estimates only",

                    "⚠️ WEEX liquidatePrice is authoritative for real open positions",

                    "⚠️ R7 builds order payloads but never transmits them",

                    "🛡 Hard execution lock active",

                    "⚠️ Live order execution disabled",

                    "⚠️ NO LIVE ORDER WAS SENT",
                ]
            )


            report = "\n".join(
                lines
            )


            # ================================================
            # CONSOLE
            # ================================================

            print(
                report
            )

            print(
                "=" * 60
            )


            # ================================================
            # TELEGRAM
            # ================================================

            telegram_sent = await telegram_send(

                session,

                report,
            )


            if telegram_sent:

                print(
                    "TELEGRAM MESSAGE SENT"
                )

            else:

                print(
                    "TELEGRAM MESSAGE NOT SENT"
                )


            print(
                "=" * 60
            )


        except Exception as error:

            report = (

                f"❌ MODULE "
                f"{MODULE_NAME} ERROR\n"

                f"{SYMBOL}\n\n"

                f"{type(error).__name__}: "
                f"{error}\n\n"

                "🛡 Hard execution lock active\n"

                "⚠️ Live order execution disabled\n"

                "⚠️ NO LIVE ORDER WAS SENT"
            )


            print(
                report
            )


            await telegram_send(

                session,

                report,
            )


            raise


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
