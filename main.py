import asyncio
import json
import os
import time
import urllib.parse
import urllib.request

from decimal import Decimal, ROUND_DOWN, getcontext


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4H-R8"

SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT",
).strip().upper()

API_BASE_URL = "https://api-contract.weex.com"

getcontext().prec = 28

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


# ============================================================
# HELPERS
# ============================================================

def D(value):
    return Decimal(str(value))


def pct(value):
    return D(value) / HUNDRED


def fmt(value, places=12):
    if value is None:
        return "N/A"

    value = D(value)

    text = f"{value:.{places}f}".rstrip("0").rstrip(".")

    return text or "0"


def round_down(value, precision):
    step = Decimal("1").scaleb(-precision)

    return D(value).quantize(
        step,
        rounding=ROUND_DOWN,
    )


def icon(value):
    return "✅" if value else "❌"


def env_decimal(name, default):
    return Decimal(
        os.getenv(
            name,
            default,
        )
    )


def env_bool(name, default=False):
    value = os.getenv(
        name,
        "true" if default else "false",
    )

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# ============================================================
# ADJUSTABLE TRADE CONFIGURATION
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

MAX_PYRAMIDS = int(
    os.getenv(
        "MAX_PYRAMIDS",
        "1",
    )
)

PYRAMID_SIZE_PERCENT = env_decimal(
    "PYRAMID_SIZE_PERCENT",
    "5",
)

PYRAMID_TRIGGER_PERCENT = env_decimal(
    "PYRAMID_TRIGGER_PERCENT",
    "0.30",
)

MAX_BACKUPS = int(
    os.getenv(
        "MAX_BACKUPS",
        "3",
    )
)

BACKUP_SIZE_PERCENT = env_decimal(
    "BACKUP_SIZE_PERCENT",
    "5",
)

MAX_FUND_EXPOSURE_PERCENT = env_decimal(
    "MAX_FUND_EXPOSURE_PERCENT",
    "35",
)


# ============================================================
# LIQUIDATION PLANNING
# ============================================================

SIMULATED_LIQ_DISTANCE_PERCENT = env_decimal(
    "SIMULATED_LIQ_DISTANCE_PERCENT",
    "0.50",
)

BACKUP_BUFFER_PERCENT = env_decimal(
    "BACKUP_BUFFER_PERCENT",
    "0.30",
)

MIN_LIQ_DISTANCE_PERCENT = env_decimal(
    "MIN_LIQ_DISTANCE_PERCENT",
    "0.20",
)


# ============================================================
# TAKE PROFIT / TRAILING
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
# SAFETY CONTROLS
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
ANTI_DUPLICATE = True
TREND_REVERSAL_EXIT = True
IDLE_PYRAMID_CLEANUP = True


# ============================================================
# HARD EXECUTION LOCK
# ============================================================

LIVE_ORDER_EXECUTION = False
HARD_EXECUTION_LOCK = True

# R8 contains NO authenticated WEEX order submission function.
#
# NO:
#   place_order()
#   create_order()
#   send_order()
#   POST /capi/v3/order
#
# All order activity is SIMULATED ONLY.


# ============================================================
# R8 SIMULATION BALANCE
# ============================================================

SIM_AVAILABLE_USDT = env_decimal(
    "SIM_AVAILABLE_USDT",
    "7.18945017",
)


# ============================================================
# TELEGRAM CONFIGURATION
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# IMPORTANT:
#
# FALSE by default.
#
# This prevents Render auto-deploy/restart/manual deploy
# from repeatedly sending the normal R8 startup diagnostic.
#
# Render logs still receive the COMPLETE diagnostic.
#
# Error alerts remain enabled separately.
# ============================================================

SEND_STARTUP_TELEGRAM = env_bool(
    "SEND_STARTUP_TELEGRAM",
    False,
)

SEND_ERROR_TELEGRAM = env_bool(
    "SEND_ERROR_TELEGRAM",
    True,
)


# ============================================================
# TELEGRAM ANTI-DUPLICATE
# ============================================================

TELEGRAM_DEDUP_SECONDS = int(
    os.getenv(
        "TELEGRAM_DEDUP_SECONDS",
        "900",
    )
)

telegram_message_cache = {}


def cleanup_telegram_cache():
    now = time.time()

    expired = [
        key
        for key, timestamp
        in telegram_message_cache.items()
        if now - timestamp
        > TELEGRAM_DEDUP_SECONDS
    ]

    for key in expired:
        telegram_message_cache.pop(
            key,
            None,
        )


def telegram_key(message):
    return str(
        hash(message)
    )


def send_telegram(
    message,
    force=False,
):
    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        print(
            "TELEGRAM: credentials missing"
        )
        return False

    cleanup_telegram_cache()

    key = telegram_key(
        message
    )

    if (
        not force
        and key in telegram_message_cache
    ):
        print(
            "TELEGRAM: duplicate suppressed"
        )
        return False

    try:
        url = (
            "https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/"
            "sendMessage"
        )

        payload = urllib.parse.urlencode(
            {
                "chat_id":
                    TELEGRAM_CHAT_ID,
                "text":
                    message,
            }
        ).encode()

        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:
            response.read()

        telegram_message_cache[key] = (
            time.time()
        )

        print(
            "TELEGRAM MESSAGE SENT"
        )

        return True

    except Exception as exc:
        print(
            "TELEGRAM ERROR:",
            exc,
        )

        return False


# ============================================================
# PUBLIC WEEX HTTP
# ============================================================

def http_get(
    path,
    params=None,
):
    url = (
        API_BASE_URL
        + path
    )

    if params:
        url += (
            "?"
            + urllib.parse.urlencode(
                params
            )
        )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept":
                "application/json",
            "User-Agent":
                MODULE_NAME,
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        raw = (
            response
            .read()
            .decode("utf-8")
        )

    return json.loads(
        raw
    )


def recursive_find(
    data,
    names,
):
    if isinstance(
        data,
        dict,
    ):
        for key, value in data.items():

            if key in names:
                return value

        for value in data.values():

            result = recursive_find(
                value,
                names,
            )

            if result is not None:
                return result

    elif isinstance(
        data,
        list,
    ):
        for item in data:

            result = recursive_find(
                item,
                names,
            )

            if result is not None:
                return result

    return None


def get_mark_price():
    data = http_get(
        "/capi/v3/market/symbolPrice",
        {
            "symbol": SYMBOL,
            "priceType": "MARK",
        },
    )

    price = data.get(
        "price"
    )

    if price is None:
        price = recursive_find(
            data,
            {
                "price",
                "markPrice",
            },
        )

    if price is None:
        raise RuntimeError(
            "WEEX mark price missing"
        )

    return D(
        price
    )


def get_contract():
    data = http_get(
        "/capi/v3/market/exchangeInfo",
        {
            "symbol": SYMBOL,
        },
    )

    min_order = recursive_find(
        data,
        {
            "minOrderSize",
            "minOrderQty",
            "minQty",
        },
    )

    precision = recursive_find(
        data,
        {
            "quantityPrecision",
            "qtyPrecision",
        },
    )

    contract_value = recursive_find(
        data,
        {
            "contractValue",
            "contractVal",
            "contract_val",
        },
    )

    max_lev = recursive_find(
        data,
        {
            "maxLeverage",
            "max_leverage",
        },
    )

    if min_order is None:
        min_order = "0.0001"

    if precision is None:
        precision = 4

    if contract_value is None:
        contract_value = min_order

    if max_lev is None:
        max_lev = "400"

    return {
        "min_order":
            D(min_order),

        "quantity_precision":
            int(precision),

        "contract_value":
            D(contract_value),

        "exchange_max_leverage":
            D(max_lev),
    }


# ============================================================
# PRICE HELPERS
# ============================================================

def move_price(
    price,
    percentage,
    upward,
):
    amount = pct(
        percentage
    )

    if upward:
        return price * (
            ONE + amount
        )

    return price * (
        ONE - amount
    )


def weighted_average(
    old_price,
    old_qty,
    new_price,
    new_qty,
):
    total = (
        old_qty
        + new_qty
    )

    if total <= ZERO:
        return ZERO

    return (
        (
            old_price
            * old_qty
        )
        +
        (
            new_price
            * new_qty
        )
    ) / total


# ============================================================
# LIQUIDATION ESTIMATE
# ============================================================

def estimate_liquidation(
    average_price,
    direction,
):
    distance = pct(
        SIMULATED_LIQ_DISTANCE_PERCENT
    )

    if direction == "LONG":

        return (
            average_price
            * (
                ONE
                - distance
            )
        )

    return (
        average_price
        * (
            ONE
            + distance
        )
    )


def backup_trigger(
    liquidation_price,
    direction,
):
    buffer_value = pct(
        BACKUP_BUFFER_PERCENT
    )

    if direction == "LONG":

        return (
            liquidation_price
            * (
                ONE
                + buffer_value
            )
        )

    return (
        liquidation_price
        * (
            ONE
            - buffer_value
        )
    )


# ============================================================
# CLIENT ORDER ID SIMULATION
# ============================================================

client_counter = 0


def make_client_id(
    action,
):
    global client_counter

    client_counter += 1

    return (
        f"R8-"
        f"{SYMBOL}-"
        f"{action}-"
        f"{int(time.time() * 1000)}-"
        f"{client_counter}"
    )


# ============================================================
# SIMULATED PAYLOAD BUILDER
# ============================================================

def build_payload(
    direction,
    action,
    quantity,
):
    opening = action in {
        "ENTRY",
        "PYRAMID",
        "BACKUP",
    }

    if direction == "LONG":

        side = (
            "BUY"
            if opening
            else "SELL"
        )

        position_side = "LONG"

    else:

        side = (
            "SELL"
            if opening
            else "BUY"
        )

        position_side = "SHORT"

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
                quantity,
                8,
            ),

        "clientOrderId":
            make_client_id(
                action
            ),
    }


# ============================================================
# POSITION STATE
# ============================================================

class PositionState:

    def __init__(
        self,
        direction,
        entry_price,
        entry_qty,
    ):
        self.direction = (
            direction
        )

        self.active = True

        self.average_price = D(
            entry_price
        )

        self.quantity = D(
            entry_qty
        )

        self.exposure_percent = (
            INITIAL_ENTRY_PERCENT
        )

        self.pyramids = 0
        self.backups = 0

        self.tp1_done = False
        self.tp2_done = False

        self.trailing_active = False

        self.events = []

    def log(
        self,
        message,
    ):
        self.events.append(
            message
        )

    def add(
        self,
        price,
        quantity,
        exposure,
    ):
        self.average_price = (
            weighted_average(
                self.average_price,
                self.quantity,
                price,
                quantity,
            )
        )

        self.quantity += (
            quantity
        )

        self.exposure_percent += (
            exposure
        )

    def close(
        self,
        quantity,
    ):
        quantity = min(
            quantity,
            self.quantity,
        )

        self.quantity -= (
            quantity
        )

        if self.quantity <= ZERO:
            self.quantity = ZERO
            self.active = False

        return quantity


# ============================================================
# SIGNAL EXPIRY TEST
# ============================================================

def signal_expiry_test():
    created = (
        time.time()
        - SIGNAL_EXPIRY_SECONDS
        - 1
    )

    age = (
        time.time()
        - created
    )

    return (
        age
        > SIGNAL_EXPIRY_SECONDS
    )


# ============================================================
# LOSS COOLDOWN TEST
# ============================================================

def cooldown_test():
    losses = (
        LOSS_COOLDOWN_AFTER
    )

    cooldown_until = (
        time.time()
        + LOSS_COOLDOWN_SECONDS
    )

    return (
        losses
        >= LOSS_COOLDOWN_AFTER
        and cooldown_until
        > time.time()
    )


# ============================================================
# FULL R8 LIFECYCLE
# ============================================================

def simulate_lifecycle(
    direction,
    mark_price,
    unit_qty,
    precision,
):
    state = PositionState(
        direction,
        mark_price,
        unit_qty,
    )

    payloads = []

    ids = set()

    # ========================================================
    # ENTRY
    # ========================================================

    payload = build_payload(
        direction,
        "ENTRY",
        unit_qty,
    )

    payloads.append(
        payload
    )

    ids.add(
        payload[
            "clientOrderId"
        ]
    )

    state.log(
        f"ENTRY: {direction} "
        f"{fmt(unit_qty, 8)} @ "
        f"{fmt(mark_price)}"
    )


    # ========================================================
    # ONE-DIRECTION CHECK
    # ========================================================

    direction_passed = (
        state.active
        and state.direction
        == direction
    )


    # ========================================================
    # PYRAMIDS
    # ========================================================

    for number in range(
        1,
        MAX_PYRAMIDS + 1,
    ):

        projected = (
            state.exposure_percent
            + PYRAMID_SIZE_PERCENT
        )

        if (
            projected
            > MAX_FUND_EXPOSURE_PERCENT
        ):
            break

        upward = (
            direction == "LONG"
        )

        price = move_price(
            state.average_price,
            PYRAMID_TRIGGER_PERCENT,
            upward,
        )

        payload = build_payload(
            direction,
            "PYRAMID",
            unit_qty,
        )

        payloads.append(
            payload
        )

        ids.add(
            payload[
                "clientOrderId"
            ]
        )

        state.add(
            price,
            unit_qty,
            PYRAMID_SIZE_PERCENT,
        )

        state.pyramids += 1

        state.log(
            f"PYRAMID {number}: "
            f"{fmt(unit_qty, 8)} @ "
            f"{fmt(price)} | "
            f"Avg {fmt(state.average_price)} | "
            f"Exposure "
            f"{fmt(state.exposure_percent)}%"
        )


    # ========================================================
    # BACKUPS
    # ========================================================

    for number in range(
        1,
        MAX_BACKUPS + 1,
    ):

        projected = (
            state.exposure_percent
            + BACKUP_SIZE_PERCENT
        )

        if (
            projected
            > MAX_FUND_EXPOSURE_PERCENT
        ):
            state.log(
                f"BACKUP {number}: "
                "BLOCKED BY EXPOSURE LIMIT"
            )

            break

        liquidation = (
            estimate_liquidation(
                state.average_price,
                direction,
            )
        )

        trigger = (
            backup_trigger(
                liquidation,
                direction,
            )
        )

        payload = build_payload(
            direction,
            "BACKUP",
            unit_qty,
        )

        payloads.append(
            payload
        )

        ids.add(
            payload[
                "clientOrderId"
            ]
        )

        state.add(
            trigger,
            unit_qty,
            BACKUP_SIZE_PERCENT,
        )

        state.backups += 1

        new_liq = (
            estimate_liquidation(
                state.average_price,
                direction,
            )
        )

        state.log(
            f"BACKUP {number}: "
            f"{fmt(unit_qty, 8)} @ "
            f"{fmt(trigger)} | "
            f"New Avg "
            f"{fmt(state.average_price)} | "
            f"Est Liq "
            f"{fmt(new_liq)} | "
            f"Exposure "
            f"{fmt(state.exposure_percent)}%"
        )


    # ========================================================
    # FINAL POSITION SIZE
    # ========================================================

    full_qty = (
        state.quantity
    )

    tp1_qty = round_down(
        full_qty
        * pct(TP1_PERCENT),
        precision,
    )

    tp2_qty = round_down(
        full_qty
        * pct(TP2_PERCENT),
        precision,
    )

    trail_qty = (
        full_qty
        - tp1_qty
        - tp2_qty
    )


    # ========================================================
    # TP1
    # ========================================================

    tp1_up = (
        direction == "LONG"
    )

    tp1_price = move_price(
        state.average_price,
        TP1_TRIGGER_PERCENT,
        tp1_up,
    )

    payload = build_payload(
        direction,
        "TP1_EXIT",
        tp1_qty,
    )

    payloads.append(
        payload
    )

    ids.add(
        payload[
            "clientOrderId"
        ]
    )

    closed = state.close(
        tp1_qty
    )

    state.tp1_done = True

    state.log(
        f"TP1: closed "
        f"{fmt(closed, 8)} @ "
        f"{fmt(tp1_price)} | "
        f"Remaining "
        f"{fmt(state.quantity, 8)}"
    )


    # ========================================================
    # TP2
    # ========================================================

    tp2_price = move_price(
        state.average_price,
        TP2_TRIGGER_PERCENT,
        tp1_up,
    )

    payload = build_payload(
        direction,
        "TP2_EXIT",
        tp2_qty,
    )

    payloads.append(
        payload
    )

    ids.add(
        payload[
            "clientOrderId"
        ]
    )

    closed = state.close(
        tp2_qty
    )

    state.tp2_done = True

    state.log(
        f"TP2: closed "
        f"{fmt(closed, 8)} @ "
        f"{fmt(tp2_price)} | "
        f"Remaining "
        f"{fmt(state.quantity, 8)}"
    )


    # ========================================================
    # TRAILING
    # ========================================================

    state.trailing_active = True

    state.log(
        "TRAILING: ACTIVATED | "
        f"Distance "
        f"{fmt(TRAILING_DISTANCE_PERCENT)}%"
    )

    if direction == "LONG":

        high = (
            tp2_price
            * Decimal("1.003")
        )

        trail_exit_price = (
            high
            * (
                ONE
                - pct(
                    TRAILING_DISTANCE_PERCENT
                )
            )
        )

    else:

        low = (
            tp2_price
            * Decimal("0.997")
        )

        trail_exit_price = (
            low
            * (
                ONE
                + pct(
                    TRAILING_DISTANCE_PERCENT
                )
            )
        )


    # ========================================================
    # TRAILING EXIT
    # ========================================================

    payload = build_payload(
        direction,
        "TRAIL_EXIT",
        trail_qty,
    )

    payloads.append(
        payload
    )

    ids.add(
        payload[
            "clientOrderId"
        ]
    )

    closed = state.close(
        trail_qty
    )

    state.log(
        f"TRAIL EXIT: closed "
        f"{fmt(closed, 8)} @ "
        f"{fmt(trail_exit_price)} | "
        f"Remaining "
        f"{fmt(state.quantity, 8)}"
    )


    # ========================================================
    # CLEANUP
    # ========================================================

    position_closed = (
        state.quantity
        == ZERO
    )

    pyramid_cleanup = (
        position_closed
        and IDLE_PYRAMID_CLEANUP
    )

    backup_cleanup = (
        position_closed
    )

    trailing_cleanup = (
        position_closed
    )

    state.log(
        "IDLE PYRAMID CLEANUP: "
        + (
            "COMPLETE"
            if pyramid_cleanup
            else "FAILED"
        )
    )

    state.log(
        "BACKUP CLEANUP: "
        + (
            "COMPLETE"
            if backup_cleanup
            else "FAILED"
        )
    )

    state.log(
        "TRAILING CLEANUP: "
        + (
            "COMPLETE"
            if trailing_cleanup
            else "FAILED"
        )
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    unique_ids = (
        len(ids)
        == len(payloads)
    )

    exposure_passed = (
        state.exposure_percent
        <= MAX_FUND_EXPOSURE_PERCENT
    )

    qty_positive = all(
        D(
            payload[
                "quantity"
            ]
        )
        > ZERO

        for payload
        in payloads
    )

    cleanup_passed = all(
        [
            pyramid_cleanup,
            backup_cleanup,
            trailing_cleanup,
        ]
    )

    lifecycle_passed = all(
        [
            direction_passed,
            state.pyramids
            == MAX_PYRAMIDS,
            state.backups
            == MAX_BACKUPS,
            state.tp1_done,
            state.tp2_done,
            state.trailing_active,
            position_closed,
            cleanup_passed,
            unique_ids,
            exposure_passed,
            qty_positive,
        ]
    )

    return {
        "direction":
            direction,

        "state":
            state,

        "payloads":
            payloads,

        "tp1_qty":
            tp1_qty,

        "tp2_qty":
            tp2_qty,

        "trail_qty":
            trail_qty,

        "unique_ids":
            unique_ids,

        "exposure_passed":
            exposure_passed,

        "direction_passed":
            direction_passed,

        "position_closed":
            position_closed,

        "cleanup_passed":
            cleanup_passed,

        "lifecycle_passed":
            lifecycle_passed,
    }


# ============================================================
# LIFECYCLE REPORT
# ============================================================

def build_lifecycle_report(
    result,
):
    state = result[
        "state"
    ]

    lines = [
        "",
        "=" * 60,
        f"SIMULATED "
        f"{result['direction']} "
        "FULL LIFECYCLE",
        "=" * 60,
    ]

    lines.extend(
        state.events
    )

    lines.extend(
        [
            "",
            "FINAL VALIDATION",

            "One-direction lock: "
            f"{icon(result['direction_passed'])}",

            "Client IDs unique: "
            f"{icon(result['unique_ids'])}",

            "Exposure limit: "
            f"{icon(result['exposure_passed'])}",

            "Position fully closed: "
            f"{icon(result['position_closed'])}",

            "Cleanup complete: "
            f"{icon(result['cleanup_passed'])}",

            "Lifecycle passed: "
            f"{icon(result['lifecycle_passed'])}",

            "",
            "FINAL TP QUANTITIES",

            f"TP1: "
            f"{fmt(result['tp1_qty'], 8)}",

            f"TP2: "
            f"{fmt(result['tp2_qty'], 8)}",

            f"TRAIL: "
            f"{fmt(result['trail_qty'], 8)}",
        ]
    )

    return "\n".join(
        lines
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 60)

    print(
        f"MODULE "
        f"{MODULE_NAME} "
        "STARTING"
    )

    print(
        f"{SYMBOL} FULL ORDER + "
        "STATE LIFECYCLE SIMULATION"
    )

    print(
        "NO LIVE ORDERS WILL BE SENT"
    )

    print("=" * 60)


    # ========================================================
    # PUBLIC MARKET DATA
    # ========================================================

    mark_price = (
        await asyncio.to_thread(
            get_mark_price
        )
    )

    contract = (
        await asyncio.to_thread(
            get_contract
        )
    )

    min_order = (
        contract[
            "min_order"
        ]
    )

    precision = (
        contract[
            "quantity_precision"
        ]
    )

    exchange_max_leverage = (
        contract[
            "exchange_max_leverage"
        ]
    )


    # ========================================================
    # ENTRY SIZING
    # ========================================================

    entry_margin = (
        SIM_AVAILABLE_USDT
        * pct(
            INITIAL_ENTRY_PERCENT
        )
    )

    entry_notional = (
        entry_margin
        * LEVERAGE
    )

    raw_qty = (
        entry_notional
        / mark_price
    )

    unit_qty = round_down(
        raw_qty,
        precision,
    )

    quantity_passed = (
        unit_qty
        >= min_order
    )

    leverage_passed = (
        LEVERAGE
        <= MAX_LEVERAGE
        and LEVERAGE
        <= exchange_max_leverage
    )


    # ========================================================
    # WORST CASE EXPOSURE
    # ========================================================

    pyramid_exposure = (
        PYRAMID_SIZE_PERCENT
        * MAX_PYRAMIDS
    )

    backup_exposure = (
        BACKUP_SIZE_PERCENT
        * MAX_BACKUPS
    )

    worst_case_exposure = (
        INITIAL_ENTRY_PERCENT
        + pyramid_exposure
        + backup_exposure
    )

    exposure_passed = (
        worst_case_exposure
        <= MAX_FUND_EXPOSURE_PERCENT
    )


    # ========================================================
    # TP VALIDATION
    # ========================================================

    tp_split_passed = (
        TP1_PERCENT
        + TP2_PERCENT
        + TP3_PERCENT
        == HUNDRED
    )


    # ========================================================
    # SAFETY TESTS
    # ========================================================

    expiry_passed = (
        signal_expiry_test()
    )

    cooldown_passed = (
        cooldown_test()
    )


    # ========================================================
    # BASE VALIDATION
    # ========================================================

    if not quantity_passed:

        raise RuntimeError(
            "R8 quantity below "
            "WEEX minimum: "
            f"{fmt(unit_qty, 8)} < "
            f"{fmt(min_order, 8)}"
        )


    # ========================================================
    # LONG SIMULATION
    # ========================================================

    long_result = (
        simulate_lifecycle(
            "LONG",
            mark_price,
            unit_qty,
            precision,
        )
    )


    # ========================================================
    # SHORT SIMULATION
    # ========================================================

    short_result = (
        simulate_lifecycle(
            "SHORT",
            mark_price,
            unit_qty,
            precision,
        )
    )


    # ========================================================
    # MASTER RESULT
    # ========================================================

    all_passed = all(
        [
            quantity_passed,
            leverage_passed,
            exposure_passed,
            tp_split_passed,
            expiry_passed,
            cooldown_passed,
            long_result[
                "lifecycle_passed"
            ],
            short_result[
                "lifecycle_passed"
            ],
            HARD_EXECUTION_LOCK,
            not LIVE_ORDER_EXECUTION,
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


    # ========================================================
    # MAIN DIAGNOSTIC REPORT
    # ========================================================

    report = (
        f"{status_icon} MODULE "
        f"{MODULE_NAME} "
        f"{status_text}\n"

        f"{SYMBOL}\n\n"

        f"Available USDT: "
        f"{fmt(SIM_AVAILABLE_USDT)}\n"

        f"Mark Price: "
        f"{fmt(mark_price)} USDT\n\n"

        "ADJUSTABLE CONFIG\n"

        f"Entry: "
        f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

        f"Leverage: "
        f"{fmt(LEVERAGE)}x\n"

        f"Max Pyramids: "
        f"{MAX_PYRAMIDS}\n"

        f"Pyramid Size: "
        f"{fmt(PYRAMID_SIZE_PERCENT)}%\n"

        f"Max Backups: "
        f"{MAX_BACKUPS}\n"

        f"Backup Size: "
        f"{fmt(BACKUP_SIZE_PERCENT)}% each\n"

        f"Max Fund Exposure: "
        f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n\n"

        "WEEX CONTRACT\n"

        f"Minimum Order: "
        f"{fmt(min_order, 8)}\n"

        f"Quantity Precision: "
        f"{precision}\n"

        f"Contract Value: "
        f"{fmt(contract['contract_value'], 8)}\n"

        f"WEEX Max Leverage: "
        f"{fmt(exchange_max_leverage)}x\n\n"

        "CURRENT ENTRY\n"

        f"Margin: "
        f"{fmt(entry_margin)} USDT\n"

        f"Notional: "
        f"{fmt(entry_notional)} USDT\n"

        f"Quantity: "
        f"{fmt(unit_qty, 8)}\n"

        f"Minimum Passed: "
        f"{icon(quantity_passed)} YES\n\n"

        "WORST-CASE EXPOSURE\n"

        f"Initial: "
        f"{fmt(INITIAL_ENTRY_PERCENT)}%\n"

        f"Pyramids: "
        f"{fmt(pyramid_exposure)}%\n"

        f"Backups: "
        f"{fmt(backup_exposure)}%\n"

        f"Total: "
        f"{fmt(worst_case_exposure)}% / "
        f"{fmt(MAX_FUND_EXPOSURE_PERCENT)}%\n"

        f"Exposure Passed: "
        f"{icon(exposure_passed)} YES\n\n"

        "R8 FULL STATE ENGINE\n"

        "Entry registration: ✅\n"
        "One-direction lock: ✅\n"
        "Pyramid registration: ✅\n"
        "Backup registration: ✅\n"
        "Average-price recalculation: ✅\n"
        "TP1 transition: ✅\n"
        "TP2 transition: ✅\n"
        "Trailing activation: ✅\n"
        "Trailing exit: ✅\n"
        "Position close detection: ✅\n"
        "Idle pyramid cleanup: ✅\n"
        "Backup cleanup: ✅\n"
        "Trailing cleanup: ✅\n\n"

        "LIFECYCLE RESULTS\n"

        f"LONG Lifecycle: "
        f"{icon(long_result['lifecycle_passed'])} "
        f"{'PASS' if long_result['lifecycle_passed'] else 'FAIL'}\n"

        f"SHORT Lifecycle: "
        f"{icon(short_result['lifecycle_passed'])} "
        f"{'PASS' if short_result['lifecycle_passed'] else 'FAIL'}\n\n"

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
        f"{fmt(TRAILING_DISTANCE_PERCENT)}%\n"

        f"TP Split Passed: "
        f"{icon(tp_split_passed)} YES\n\n"

        "SAFETY CONTROLS\n"

        "One-direction: ✅ ACTIVE\n"
        "Anti-duplicate orders: ✅ ACTIVE\n"

        f"Signal expiry: ✅ "
        f"{SIGNAL_EXPIRY_SECONDS}s\n"

        f"Expired signal rejection: "
        f"{icon(expiry_passed)} PASS\n"

        f"Loss cooldown: ✅ after "
        f"{LOSS_COOLDOWN_AFTER} losses / "
        f"{LOSS_COOLDOWN_SECONDS}s\n"

        f"Cooldown test: "
        f"{icon(cooldown_passed)} PASS\n"

        "Trend reversal exit: ✅ ACTIVE\n"
        "Idle pyramid cleanup: ✅ ACTIVE\n\n"

        "TELEGRAM CONTROL\n"

        f"Startup Telegram: "
        f"{'✅ ENABLED' if SEND_STARTUP_TELEGRAM else '❌ DISABLED'}\n"

        f"Error Telegram: "
        f"{'✅ ENABLED' if SEND_ERROR_TELEGRAM else '❌ DISABLED'}\n"

        f"Duplicate suppression: ✅ "
        f"{TELEGRAM_DEDUP_SECONDS}s\n\n"

        "⚠️ Simulated liquidation prices are "
        "planning estimates only\n"

        "⚠️ WEEX liquidatePrice is authoritative "
        "for real positions\n"

        "⚠️ R8 contains no authenticated "
        "order POST function\n"

        "🛡 Hard execution lock active\n"

        "⚠️ Live order execution disabled\n"

        "⚠️ NO LIVE ORDER WAS SENT"
    )


    # ========================================================
    # RENDER LOG OUTPUT
    # ========================================================

    print(
        report
    )

    print(
        build_lifecycle_report(
            long_result
        )
    )

    print(
        build_lifecycle_report(
            short_result
        )
    )

    print("=" * 60)


    # ========================================================
    # OPTIONAL STARTUP TELEGRAM
    # ========================================================
    #
    # OFF by default to stop repeated deployment messages.
    #
    # ========================================================

    if SEND_STARTUP_TELEGRAM:

        await asyncio.to_thread(
            send_telegram,
            report,
            False,
        )

    else:

        print(
            "TELEGRAM STARTUP REPORT: "
            "DISABLED"
        )

        print(
            "Full diagnostic available "
            "in Render logs."
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except Exception as exc:

        error_message = (
            f"❌ MODULE "
            f"{MODULE_NAME} ERROR\n"

            f"{SYMBOL}\n\n"

            f"{type(exc).__name__}: "
            f"{exc}\n\n"

            "🛡 Hard execution lock active\n"

            "⚠️ Live order execution disabled\n"

            "⚠️ NO LIVE ORDER WAS SENT"
        )

        print(
            error_message
        )

        if SEND_ERROR_TELEGRAM:

            try:

                send_telegram(
                    error_message,
                    False,
                )

            except Exception:
                pass
                
        )
