import asyncio
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import aiohttp
import websockets
from telegram import Bot


MODULE_NAME = "0F-4B"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").strip().upper()

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"
SUBSCRIPTION_CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"

HISTORICAL_URL = (
    "https://api-contract.weex.com"
    "/capi/v3/market/klines"
)

HISTORICAL_LIMIT = 250

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


def env_decimal(name: str, default: str) -> Decimal:
    raw = os.getenv(name, default).strip()

    try:
        return Decimal(raw)

    except (InvalidOperation, TypeError):

        print(
            f"CONFIG WARNING: "
            f"{name}={raw!r} invalid; "
            f"using {default}"
        )

        return Decimal(default)


def env_int(
    name: str,
    default: int,
) -> int:

    raw = os.getenv(
        name,
        str(default),
    ).strip()

    try:
        return int(raw)

    except (ValueError, TypeError):

        print(
            f"CONFIG WARNING: "
            f"{name}={raw!r} invalid; "
            f"using {default}"
        )

        return default


def env_bool(
    name: str,
    default: bool,
) -> bool:

    raw = os.getenv(
        name,
        "true" if default else "false",
    ).strip().lower()

    return raw in {
        "1",
        "true",
        "yes",
        "on",
        "y",
    }


EMA_FAST = env_int(
    "EMA_FAST",
    19,
)

EMA_MID = env_int(
    "EMA_MID",
    50,
)

EMA_SLOW = env_int(
    "EMA_SLOW",
    200,
)


INITIAL_ENTRY_PERCENT = env_decimal(
    "INITIAL_ENTRY_PERCENT",
    "5",
)

LEVERAGE = env_decimal(
    "LEVERAGE",
    "5",
)

MAX_LEVERAGE = env_decimal(
    "MAX_LEVERAGE",
    "10",
)


MAX_PYRAMID_ADDS = max(
    0,
    env_int(
        "MAX_PYRAMID_ADDS",
        1,
    ),
)


PYRAMID_1_PERCENT = env_decimal(
    "PYRAMID_1_PERCENT",
    "5",
)

PYRAMID_2_PERCENT = env_decimal(
    "PYRAMID_2_PERCENT",
    "5",
)

PYRAMID_3_PERCENT = env_decimal(
    "PYRAMID_3_PERCENT",
    "5",
)


PYRAMID_TRIGGER_PERCENT = env_decimal(
    "PYRAMID_TRIGGER_PERCENT",
    "0.20",
)


PYRAMID_EXPIRY_SECONDS = max(
    60,
    env_int(
        "PYRAMID_EXPIRY_SECONDS",
        900,
    ),
)


MAX_BACKUPS = max(
    0,
    env_int(
        "MAX_BACKUPS",
        3,
    ),
)


BACKUP_1_PERCENT = env_decimal(
    "BACKUP_1_PERCENT",
    "5",
)

BACKUP_2_PERCENT = env_decimal(
    "BACKUP_2_PERCENT",
    "5",
)

BACKUP_3_PERCENT = env_decimal(
    "BACKUP_3_PERCENT",
    "5",
)


BACKUP_LIQUIDATION_BUFFER_PERCENT = (
    env_decimal(
        "BACKUP_LIQUIDATION_BUFFER_PERCENT",
        "2",
    )
)


MIN_LIQUIDATION_DISTANCE_PERCENT = (
    env_decimal(
        "MIN_LIQUIDATION_DISTANCE_PERCENT",
        "3",
    )
)


MAX_FUND_EXPOSURE_PERCENT = env_decimal(
    "MAX_FUND_EXPOSURE_PERCENT",
    "35",
)


MAX_TOTAL_LEVERAGE_EXPOSURE = env_decimal(
    "MAX_TOTAL_LEVERAGE_EXPOSURE",
    "10",
)


MAX_TRADE_LOSS_PERCENT = env_decimal(
    "MAX_TRADE_LOSS_PERCENT",
    "10",
)


SIGNAL_EXPIRY_SECONDS = max(
    60,
    env_int(
        "SIGNAL_EXPIRY_SECONDS",
        300,
    ),
)


LOSS_COOLDOWN_SECONDS = max(
    0,
    env_int(
        "LOSS_COOLDOWN_SECONDS",
        900,
    ),
)


MAX_CONSECUTIVE_LOSSES = max(
    1,
    env_int(
        "MAX_CONSECUTIVE_LOSSES",
        2,
    ),
)


TP1_PERCENT_OF_POSITION = env_decimal(
    "TP1_PERCENT_OF_POSITION",
    "20",
)

TP2_PERCENT_OF_POSITION = env_decimal(
    "TP2_PERCENT_OF_POSITION",
    "20",
)

TP3_PERCENT_OF_POSITION = env_decimal(
    "TP3_PERCENT_OF_POSITION",
    "60",
)


TP1_PROFIT_PERCENT = env_decimal(
    "TP1_PROFIT_PERCENT",
    "0.50",
)


TP2_PROFIT_PERCENT = env_decimal(
    "TP2_PROFIT_PERCENT",
    "1.00",
)


TRAILING_DISTANCE_PERCENT = env_decimal(
    "TRAILING_DISTANCE_PERCENT",
    "0.25",
)


MIN_EMA_19_50_SEPARATION_PERCENT = (
    env_decimal(
        "MIN_EMA_19_50_SEPARATION_PERCENT",
        "0.01",
    )
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


SIMULATED_ACCOUNT_EQUITY_USDT = (
    env_decimal(
        "SIMULATED_ACCOUNT_EQUITY_USDT",
        "1000",
    )
)


LIVE_ORDER_EXECUTION = False


PYRAMID_PERCENTS = [
    PYRAMID_1_PERCENT,
    PYRAMID_2_PERCENT,
    PYRAMID_3_PERCENT,
]


BACKUP_PERCENTS = [
    BACKUP_1_PERCENT,
    BACKUP_2_PERCENT,
    BACKUP_3_PERCENT,
]


D0 = Decimal("0")
D100 = Decimal("100")


def pct(
    value: Decimal,
) -> Decimal:

    return value / D100


def d(
    value: Any,
    default: Decimal = D0,
) -> Decimal:

    try:
        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        return default


def fmt(
    value: Decimal,
    places: int = 4,
) -> str:

    q = Decimal(1).scaleb(
        -places
    )

    try:
        return (
            f"{value.quantize(q):f}"
        )

    except Exception:
        return str(value)


def now_ts() -> float:

    return time.time()


def log_bar() -> None:

    print(
        "=" * 60
    )


def telegram_is_configured() -> bool:

    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(
    text: str,
) -> None:

    if not telegram_is_configured():

        return

    try:

        bot = Bot(
            token=TELEGRAM_BOT_TOKEN
        )

        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=text,
        )

        print(
            "TELEGRAM MESSAGE SENT"
        )

    except Exception as exc:

        print(
            "TELEGRAM ERROR:",
            type(exc).__name__,
            exc,
        )


def ema_series(
    values: list[Decimal],
    period: int,
) -> Optional[Decimal]:

    if len(values) < period:

        return None

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    seed = (
        sum(
            values[:period]
        )
        / Decimal(period)
    )

    ema = seed

    for price in values[period:]:

        ema = (
            (price - ema)
            * multiplier
            + ema
        )

    return ema


def calculate_emas(
    closes: list[Decimal],
):

    return (
        ema_series(
            closes,
            EMA_FAST,
        ),
        ema_series(
            closes,
            EMA_MID,
        ),
        ema_series(
            closes,
            EMA_SLOW,
        ),
    )


def structure_label(
    ema_fast: Decimal,
    ema_mid: Decimal,
    ema_slow: Decimal,
) -> str:

    if (
        ema_fast
        > ema_mid
        > ema_slow
    ):

        return "STRONG_BULLISH"

    if (
        ema_fast
        < ema_mid
        < ema_slow
    ):

        return "STRONG_BEARISH"

    if ema_fast > ema_mid:

        return "EARLY_BULLISH"

    if ema_fast < ema_mid:

        return "EARLY_BEARISH"

    return "NEUTRAL"


def direction_from_structure(
    structure: str,
) -> Optional[str]:

    if structure == "STRONG_BULLISH":

        return "LONG"

    if structure == "STRONG_BEARISH":

        return "SHORT"

    return None


def ema_separation_percent(
    price: Decimal,
    ema_fast: Decimal,
    ema_mid: Decimal,
) -> Decimal:

    if price <= 0:

        return D0

    return (
        abs(
            ema_fast
            - ema_mid
        )
        / price
        * D100
    )


@dataclass
class PlannedAdd:

    plan_id: str

    kind: str

    slot: int

    side: str

    allocation_percent: Decimal

    trigger_price: Decimal

    created_at: float

    expires_at: Optional[float]

    status: str = "PENDING"

    reason: str = ""


@dataclass
class PositionState:

    side: Optional[str] = None

    entry_price: Decimal = D0

    quantity: Decimal = D0

    margin_used: Decimal = D0

    notional: Decimal = D0

    last_add_price: Decimal = D0

    estimated_liquidation_price: Decimal = D0

    opened_at: Optional[float] = None

    signal_created_at: Optional[float] = None

    pyramid_adds_filled: int = 0

    backups_filled: int = 0

    tp1_done: bool = False

    tp2_done: bool = False

    trailing_active: bool = False

    trailing_peak: Decimal = D0

    trailing_trough: Decimal = D0

    realized_pnl: Decimal = D0

    consecutive_losses: int = 0

    cooldown_until: float = 0.0

    active_plans: list[
        PlannedAdd
    ] = field(
        default_factory=list
    )

    recent_order_keys: set[
        str
    ] = field(
        default_factory=set
    )

    def is_open(
        self,
    ) -> bool:

        return bool(
            self.side
            and self.quantity > 0
        )


STATE = PositionState()


def allocation_to_margin(
    allocation_percent: Decimal,
) -> Decimal:

    return (
        SIMULATED_ACCOUNT_EQUITY_USDT
        * pct(
            allocation_percent
        )
    )


def margin_to_notional(
    margin: Decimal,
    leverage: Decimal,
) -> Decimal:

    return (
        margin
        * leverage
    )


def quantity_for_notional(
    notional: Decimal,
    price: Decimal,
) -> Decimal:

    if price <= 0:

        return D0

    return (
        notional
        / price
    )


def fund_exposure_percent(
    margin_used: Decimal,
) -> Decimal:

    if (
        SIMULATED_ACCOUNT_EQUITY_USDT
        <= 0
    ):

        return Decimal(
            "999999"
        )

    return (
        margin_used
        / SIMULATED_ACCOUNT_EQUITY_USDT
        * D100
    )


def effective_leverage_exposure(
    notional: Decimal,
) -> Decimal:

    if (
        SIMULATED_ACCOUNT_EQUITY_USDT
        <= 0
    ):

        return Decimal(
            "999999"
        )

    return (
        notional
        / SIMULATED_ACCOUNT_EQUITY_USDT
    )


def estimate_liquidation_price(
    side: str,
    avg_entry: Decimal,
    leverage: Decimal,
) -> Decimal:

    if (
        avg_entry <= 0
        or leverage <= 0
    ):

        return D0

    maintenance_allowance = (
        Decimal("0.005")
    )

    move = (
        Decimal("1")
        / leverage
    ) - maintenance_allowance

    move = max(
        move,
        Decimal("0.001"),
    )

    if side == "LONG":

        return max(
            D0,
            avg_entry
            * (
                Decimal("1")
                - move
            ),
        )

    return (
        avg_entry
        * (
            Decimal("1")
            + move
        )
    )


def liquidation_distance_percent(
    side: str,
    mark_price: Decimal,
    liquidation_price: Decimal,
) -> Decimal:

    if (
        mark_price <= 0
        or liquidation_price <= 0
    ):

        return D0

    if side == "LONG":

        return max(
            D0,
            (
                mark_price
                - liquidation_price
            )
            / mark_price
            * D100,
        )

    return max(
        D0,
        (
            liquidation_price
            - mark_price
        )
        / mark_price
        * D100,
    )


def unrealized_pnl(
    position: PositionState,
    mark_price: Decimal,
) -> Decimal:

    if (
        not position.is_open()
        or position.entry_price <= 0
    ):

        return D0

    if position.side == "LONG":

        return (
            mark_price
            - position.entry_price
        ) * position.quantity

    return (
        position.entry_price
        - mark_price
    ) * position.quantity


def current_trade_loss_percent(
    position: PositionState,
    mark_price: Decimal,
) -> Decimal:

    pnl = unrealized_pnl(
        position,
        mark_price,
    )

    if (
        pnl >= 0
        or SIMULATED_ACCOUNT_EQUITY_USDT
        <= 0
    ):

        return D0

    return (
        abs(pnl)
        / SIMULATED_ACCOUNT_EQUITY_USDT
        * D100
    )


def safety_check_new_add(
    allocation_percent: Decimal,
    mark_price: Decimal,
):

    if allocation_percent <= 0:

        return (
            False,
            "allocation is zero",
        )

    if LEVERAGE <= 0:

        return (
            False,
            "leverage must be positive",
        )

    if LEVERAGE > MAX_LEVERAGE:

        return (
            False,
            (
                f"configured leverage "
                f"{LEVERAGE}x exceeds "
                f"MAX_LEVERAGE "
                f"{MAX_LEVERAGE}x"
            ),
        )

    extra_margin = (
        allocation_to_margin(
            allocation_percent
        )
    )

    extra_notional = (
        margin_to_notional(
            extra_margin,
            LEVERAGE,
        )
    )

    proposed_margin = (
        STATE.margin_used
        + extra_margin
    )

    proposed_notional = (
        STATE.notional
        + extra_notional
    )

    proposed_fund_exposure = (
        fund_exposure_percent(
            proposed_margin
        )
    )

    if (
        proposed_fund_exposure
        > MAX_FUND_EXPOSURE_PERCENT
    ):

        return (
            False,
            (
                f"fund exposure "
                f"{fmt(proposed_fund_exposure, 2)}% "
                f"> "
                f"{fmt(MAX_FUND_EXPOSURE_PERCENT, 2)}%"
            ),
        )

    proposed_leverage_exposure = (
        effective_leverage_exposure(
            proposed_notional
        )
    )

    if (
        proposed_leverage_exposure
        > MAX_TOTAL_LEVERAGE_EXPOSURE
    ):

        return (
            False,
            (
                f"total leverage exposure "
                f"{fmt(proposed_leverage_exposure, 2)}x "
                f"> "
                f"{fmt(MAX_TOTAL_LEVERAGE_EXPOSURE, 2)}x"
            ),
        )

    if STATE.is_open():

        loss_percent = (
            current_trade_loss_percent(
                STATE,
                mark_price,
            )
        )

        if (
            loss_percent
            >= MAX_TRADE_LOSS_PERCENT
        ):

            return (
                False,
                (
                    f"trade loss "
                    f"{fmt(loss_percent, 2)}% "
                    f">= max "
                    f"{fmt(MAX_TRADE_LOSS_PERCENT, 2)}%"
                ),
            )

    return (
        True,
        "OK",
    )


def cancel_plans(
    kind: Optional[str],
    reason: str,
) -> int:

    cancelled = 0

    for plan in STATE.active_plans:

        if (
            plan.status
            != "PENDING"
        ):

            continue

        if (
            kind is not None
            and plan.kind != kind
        ):

            continue

        plan.status = (
            "CANCELLED"
        )

        plan.reason = reason

        cancelled += 1

    if cancelled:

        print(
            "PLAN CLEANUP:",
            f"cancelled {cancelled}",
            kind or "ALL",
            "pending plan(s)",
            f"| reason={reason}",
        )

    return cancelled


def cleanup_expired_idle_pyramids(
    current_time: float,
) -> int:

    cleaned = 0

    for plan in STATE.active_plans:

        if (
            plan.kind == "PYRAMID"
            and plan.status == "PENDING"
            and plan.expires_at is not None
            and current_time
            >= plan.expires_at
        ):

            plan.status = (
                "EXPIRED"
            )

            plan.reason = (
                "idle pyramid expired"
            )

            cleaned += 1

    if cleaned:

        print(
            "IDLE PYRAMID CLEANUP:",
            f"expired {cleaned}",
            "stale pyramid plan(s)",
        )

    return cleaned


def prune_finished_plans() -> None:

    if len(
        STATE.active_plans
    ) > 100:

        STATE.active_plans[:] = (
            STATE.active_plans[-50:]
        )


def pending_plan(
    kind: str,
    slot: Optional[int] = None,
) -> Optional[PlannedAdd]:

    for plan in STATE.active_plans:

        if (
            plan.kind != kind
            or plan.status != "PENDING"
        ):

            continue

        if (
            slot is None
            or plan.slot == slot
        ):

            return plan

    return None


def make_order_key(
    kind: str,
    slot: int,
    side: str,
) -> str:

    return (
        f"{kind}:"
        f"{slot}:"
        f"{side}"
    )


def anti_duplicate_allowed(
    kind: str,
    slot: int,
    side: str,
) -> bool:

    if not ANTI_DUPLICATE_ORDERS:

        return True

    key = make_order_key(
        kind,
        slot,
        side,
    )

    return (
        key
        not in STATE.recent_order_keys
    )


def mark_order_key(
    kind: str,
    slot: int,
    side: str,
) -> None:

    if ANTI_DUPLICATE_ORDERS:

        STATE.recent_order_keys.add(
            make_order_key(
                kind,
                slot,
                side,
            )
        )


def weighted_entry_after_add(
    current_qty: Decimal,
    current_entry: Decimal,
    add_qty: Decimal,
    add_price: Decimal,
) -> Decimal:

    total_qty = (
        current_qty
        + add_qty
    )

    if total_qty <= 0:

        return D0

    return (
        (
            current_qty
            * current_entry
        )
        +
        (
            add_qty
            * add_price
        )
    ) / total_qty


def execute_simulated_add(
    kind: str,
    slot: int,
    allocation_percent: Decimal,
    price: Decimal,
):

    if LIVE_ORDER_EXECUTION:

        return (
            False,
            (
                "0F-4B live execution "
                "hard-lock unexpectedly disabled"
            ),
        )

    ok, reason = (
        safety_check_new_add(
            allocation_percent,
            price,
        )
    )

    if not ok:

        return (
            False,
            reason,
        )

    side = STATE.side

    if not side:

        return (
            False,
            "no open position",
        )

    if not anti_duplicate_allowed(
        kind,
        slot,
        side,
    ):

        return (
            False,
            "anti-duplicate protection",
        )

    margin = (
        allocation_to_margin(
            allocation_percent
        )
    )

    notional = (
        margin_to_notional(
            margin,
            LEVERAGE,
        )
    )

    add_qty = (
        quantity_for_notional(
            notional,
            price,
        )
    )

    if add_qty <= 0:

        return (
            False,
            "calculated quantity is zero",
        )

    new_entry = (
        weighted_entry_after_add(
            STATE.quantity,
            STATE.entry_price,
            add_qty,
            price,
        )
    )

    STATE.quantity += (
        add_qty
    )

    STATE.margin_used += (
        margin
    )

    STATE.notional += (
        notional
    )

    STATE.entry_price = (
        new_entry
    )

    STATE.last_add_price = (
        price
    )

    STATE.estimated_liquidation_price = (
        estimate_liquidation_price(
            side,
            STATE.entry_price,
            LEVERAGE,
        )
    )

    if kind == "PYRAMID":

        STATE.pyramid_adds_filled += 1

    elif kind == "BACKUP":

        STATE.backups_filled += 1

    mark_order_key(
        kind,
        slot,
        side,
    )

    log_bar()

    print(
        f"SIMULATED {kind} EXECUTED"
    )

    print(
        f"SLOT: {slot}"
    )

    print(
        f"SIDE: {side}"
    )

    print(
        f"PRICE: "
        f"{fmt(price, 2)}"
    )

    print(
        f"ALLOCATION: "
        f"{fmt(allocation_percent, 2)}%"
    )

    print(
        f"NEW AVG ENTRY: "
        f"{fmt(STATE.entry_price, 2)}"
    )

    print(
        f"TOTAL MARGIN: "
        f"{fmt(STATE.margin_used, 2)} USDT"
    )

    print(
        f"TOTAL NOTIONAL: "
        f"{fmt(STATE.notional, 2)} USDT"
    )

    print(
        f"NEW EST. LIQUIDATION: "
        f"{fmt(STATE.estimated_liquidation_price, 2)}"
    )

    log_bar()

    return (
        True,
        "executed",
    )


def open_simulated_position(
    side: str,
    price: Decimal,
):

    if STATE.is_open():

        if (
            ONE_DIRECTION_ONLY
            and STATE.side != side
        ):

            return (
                False,
                "one-direction-only protection",
            )

        return (
            False,
            "position already open",
        )

    if (
        now_ts()
        < STATE.cooldown_until
    ):

        return (
            False,
            "loss cooldown active",
        )

    ok, reason = (
        safety_check_new_add(
            INITIAL_ENTRY_PERCENT,
            price,
        )
    )

    if not ok:

        return (
            False,
            reason,
        )

    margin = (
        allocation_to_margin(
            INITIAL_ENTRY_PERCENT
        )
    )

    notional = (
        margin_to_notional(
            margin,
            LEVERAGE,
        )
    )

    qty = (
        quantity_for_notional(
            notional,
            price,
        )
    )

    if qty <= 0:

        return (
            False,
            "calculated entry quantity is zero",
        )

    STATE.side = side

    STATE.entry_price = (
        price
    )

    STATE.quantity = qty

    STATE.margin_used = (
        margin
    )

    STATE.notional = (
        notional
    )

    STATE.last_add_price = (
        price
    )

    STATE.estimated_liquidation_price = (
        estimate_liquidation_price(
            side,
            price,
            LEVERAGE,
        )
    )

    STATE.opened_at = (
        now_ts()
    )

    STATE.signal_created_at = (
        now_ts()
    )

    STATE.pyramid_adds_filled = 0

    STATE.backups_filled = 0

    STATE.tp1_done = False

    STATE.tp2_done = False

    STATE.trailing_active = False

    STATE.trailing_peak = price

    STATE.trailing_trough = price

    STATE.realized_pnl = D0

    STATE.active_plans.clear()

    STATE.recent_order_keys.clear()

    log_bar()

    print(
        "SIMULATED INITIAL POSITION OPENED"
    )

    print(
        f"SIDE: {side}"
    )

    print(
        f"PRICE: "
        f"{fmt(price, 2)}"
    )

    print(
        f"ENTRY ALLOCATION: "
        f"{fmt(INITIAL_ENTRY_PERCENT, 2)}%"
    )

    print(
        f"LEVERAGE: "
        f"{fmt(LEVERAGE, 2)}x"
    )

    print(
        f"MARGIN: "
        f"{fmt(margin, 2)} USDT"
    )

    print(
        f"NOTIONAL: "
        f"{fmt(notional, 2)} USDT"
    )

    print(
        f"QUANTITY: "
        f"{fmt(qty, 8)}"
    )

    print(
        "EST. LIQUIDATION:",
        fmt(
            STATE.estimated_liquidation_price,
            2,
        ),
        "(LOCAL SIMULATION ONLY)",
    )

    log_bar()

    return (
        True,
        "opened",
    )


def close_fraction(
    fraction_percent: Decimal,
    price: Decimal,
    reason: str,
) -> Decimal:

    if (
        not STATE.is_open()
        or fraction_percent <= 0
    ):

        return D0

    fraction = min(
        Decimal("1"),
        pct(
            fraction_percent
        ),
    )

    qty_to_close = (
        STATE.quantity
        * fraction
    )

    if STATE.side == "LONG":

        pnl = (
            price
            - STATE.entry_price
        ) * qty_to_close

    else:

        pnl = (
            STATE.entry_price
            - price
        ) * qty_to_close

    STATE.quantity -= (
        qty_to_close
    )

    STATE.notional -= (
        STATE.notional
        * fraction
    )

    STATE.margin_used -= (
        STATE.margin_used
        * fraction
    )

    STATE.realized_pnl += (
        pnl
    )

    print(
        "SIMULATED PARTIAL CLOSE",
        f"| {reason}",
        f"| {fmt(fraction_percent, 2)}%",
        f"| PNL={fmt(pnl, 4)} USDT",
    )

    if (
        STATE.quantity
        <= Decimal("0.0000000001")
    ):

        close_entire_position(
            price,
            reason,
        )

    return pnl


def close_entire_position(
    price: Decimal,
    reason: str,
) -> None:

    if not STATE.is_open():

        return

    remaining_qty = (
        STATE.quantity
    )

    if STATE.side == "LONG":

        pnl = (
            price
            - STATE.entry_price
        ) * remaining_qty

    else:

        pnl = (
            STATE.entry_price
            - price
        ) * remaining_qty

    STATE.realized_pnl += (
        pnl
    )

    total_trade_pnl = (
        STATE.realized_pnl
    )

    cancel_plans(
        None,
        (
            f"position closed: "
            f"{reason}"
        ),
    )

    if total_trade_pnl < 0:

        STATE.consecutive_losses += 1

        if (
            STATE.consecutive_losses
            >= MAX_CONSECUTIVE_LOSSES
        ):

            STATE.cooldown_until = (
                now_ts()
                + LOSS_COOLDOWN_SECONDS
            )

            print(
                "LOSS COOLDOWN ACTIVATED:",
                f"{LOSS_COOLDOWN_SECONDS}s",
            )

    else:

        STATE.consecutive_losses = 0

    log_bar()

    print(
        "SIMULATED POSITION CLOSED"
    )

    print(
        f"REASON: {reason}"
    )

    print(
        f"EXIT PRICE: "
        f"{fmt(price, 2)}"
    )

    print(
        f"TRADE PNL: "
        f"{fmt(total_trade_pnl, 4)} USDT"
    )

    print(
        "CONSECUTIVE LOSSES:",
        STATE.consecutive_losses,
    )

    log_bar()

    consecutive_losses = (
        STATE.consecutive_losses
    )

    cooldown_until = (
        STATE.cooldown_until
    )

    STATE.side = None

    STATE.entry_price = D0

    STATE.quantity = D0

    STATE.margin_used = D0

    STATE.notional = D0

    STATE.last_add_price = D0

    STATE.estimated_liquidation_price = D0

    STATE.opened_at = None

    STATE.signal_created_at = None

    STATE.pyramid_adds_filled = 0

    STATE.backups_filled = 0

    STATE.tp1_done = False

    STATE.tp2_done = False

    STATE.trailing_active = False

    STATE.trailing_peak = D0

    STATE.trailing_trough = D0

    STATE.realized_pnl = D0

    STATE.active_plans.clear()

    STATE.recent_order_keys.clear()

    STATE.consecutive_losses = (
        consecutive_losses
    )

    STATE.cooldown_until = (
        cooldown_until
    )


def favorable_trigger_price(
    side: str,
    anchor: Decimal,
) -> Decimal:

    move = pct(
        PYRAMID_TRIGGER_PERCENT
    )

    if side == "LONG":

        return (
            anchor
            * (
                Decimal("1")
                + move
            )
        )

    return (
        anchor
        * (
            Decimal("1")
            - move
        )
    )


def ensure_next_pyramid_plan(
    price: Decimal,
    strong_trend_side: Optional[str],
) -> None:

    cleanup_expired_idle_pyramids(
        now_ts()
    )

    if not STATE.is_open():

        cancel_plans(
            "PYRAMID",
            "no open position",
        )

        return

    if (
        strong_trend_side
        != STATE.side
    ):

        cancel_plans(
            "PYRAMID",
            (
                "momentum/trend "
                "no longer confirms position"
            ),
        )

        return

    if (
        STATE.backups_filled > 0
        or pending_plan(
            "BACKUP"
        )
        is not None
    ):

        cancel_plans(
            "PYRAMID",
            "backup sequence active",
        )

        return

    if (
        STATE.pyramid_adds_filled
        >= MAX_PYRAMID_ADDS
    ):

        cancel_plans(
            "PYRAMID",
            "maximum pyramid adds reached",
        )

        return

    slot = (
        STATE.pyramid_adds_filled
        + 1
    )

    if (
        slot
        > len(
            PYRAMID_PERCENTS
        )
    ):

        return

    if (
        pending_plan(
            "PYRAMID",
            slot,
        )
        is not None
    ):

        return

    allocation = (
        PYRAMID_PERCENTS[
            slot - 1
        ]
    )

    ok, reason = (
        safety_check_new_add(
            allocation,
            price,
        )
    )

    if not ok:

        cancel_plans(
            "PYRAMID",
            f"safety lock: {reason}",
        )

        return

    if (
        STATE.last_add_price
        > 0
    ):

        anchor = (
            STATE.last_add_price
        )

    else:

        anchor = (
            STATE.entry_price
        )

    trigger = (
        favorable_trigger_price(
            STATE.side,
            anchor,
        )
    )

    plan = PlannedAdd(
        plan_id=str(
            uuid.uuid4()
        ),
        kind="PYRAMID",
        slot=slot,
        side=STATE.side,
        allocation_percent=allocation,
        trigger_price=trigger,
        created_at=now_ts(),
        expires_at=(
            now_ts()
            + PYRAMID_EXPIRY_SECONDS
        ),
    )

    STATE.active_plans.append(
        plan
    )

    print(
        "PYRAMID PLAN CREATED",
        f"| slot={slot}",
        f"| allocation={fmt(allocation, 2)}%",
        f"| trigger={fmt(trigger, 2)}",
        f"| expires={PYRAMID_EXPIRY_SECONDS}s",
    )


def maybe_execute_pyramid(
    price: Decimal,
    strong_trend_side: Optional[str],
) -> None:

    cleanup_expired_idle_pyramids(
        now_ts()
    )

    if not STATE.is_open():

        return

    if (
        strong_trend_side
        != STATE.side
    ):

        cancel_plans(
            "PYRAMID",
            (
                "trend confirmation "
                "lost before fill"
            ),
        )

        return

    plan = pending_plan(
        "PYRAMID"
    )

    if not plan:

        return

    if STATE.side == "LONG":

        triggered = (
            price
            >= plan.trigger_price
        )

    else:

        triggered = (
            price
            <= plan.trigger_price
        )

    if not triggered:

        return

    ok, reason = (
        execute_simulated_add(
            "PYRAMID",
            plan.slot,
            plan.allocation_percent,
            price,
        )
    )

    if ok:

        plan.status = (
            "FILLED"
        )

        plan.reason = (
            "momentum trigger reached"
        )

    else:

        plan.status = (
            "CANCELLED"
        )

        plan.reason = (
            reason
        )

        print(
            f"PYRAMID BLOCKED: "
            f"{reason}"
        )


def backup_trigger_from_liquidation(
    side: str,
    liquidation: Decimal,
) -> Decimal:

    buffer_fraction = pct(
        BACKUP_LIQUIDATION_BUFFER_PERCENT
    )

    if side == "LONG":

        return (
            liquidation
            * (
                Decimal("1")
                + buffer_fraction
            )
        )

    return (
        liquidation
        * (
            Decimal("1")
            - buffer_fraction
        )
    )


def ensure_next_backup_plan(
    mark_price: Decimal,
) -> None:

    if not STATE.is_open():

        cancel_plans(
            "BACKUP",
            "no open position",
        )

        return

    if (
        STATE.backups_filled
        >= MAX_BACKUPS
    ):

        cancel_plans(
            "BACKUP",
            "maximum backups reached",
        )

        return

    slot = (
        STATE.backups_filled
        + 1
    )

    if (
        slot
        > len(
            BACKUP_PERCENTS
        )
    ):

        return

    if (
        pending_plan(
            "BACKUP",
            slot,
        )
        is not None
    ):

        return

    liquidation = (
        STATE.estimated_liquidation_price
    )

    if liquidation <= 0:

        return

    distance = (
        liquidation_distance_percent(
            STATE.side,
            mark_price,
            liquidation,
        )
    )

    if (
        distance
        < MIN_LIQUIDATION_DISTANCE_PERCENT
    ):

        cancel_plans(
            "PYRAMID",
            "liquidation safety lock",
        )

        print(
            "BACKUP NOT PLANNED:",
            "liquidation distance",
            f"{fmt(distance, 2)}%",
            "< minimum",
            f"{fmt(MIN_LIQUIDATION_DISTANCE_PERCENT, 2)}%",
        )

        return

    allocation = (
        BACKUP_PERCENTS[
            slot - 1
        ]
    )

    ok, reason = (
        safety_check_new_add(
            allocation,
            mark_price,
        )
    )

    if not ok:

        cancel_plans(
            "PYRAMID",
            (
                f"backup safety "
                f"takeover: {reason}"
            ),
        )

        print(
            f"BACKUP PLAN BLOCKED: "
            f"{reason}"
        )

        return

    trigger = (
        backup_trigger_from_liquidation(
            STATE.side,
            liquidation,
        )
    )

    plan = PlannedAdd(
        plan_id=str(
            uuid.uuid4()
        ),
        kind="BACKUP",
        slot=slot,
        side=STATE.side,
        allocation_percent=allocation,
        trigger_price=trigger,
        created_at=now_ts(),
        expires_at=None,
    )

    STATE.active_plans.append(
        plan
    )

    print(
        "BACKUP PLAN CREATED",
        f"| slot={slot}",
        f"| allocation={fmt(allocation, 2)}%",
        f"| est_liq={fmt(liquidation, 2)}",
        f"| trigger={fmt(trigger, 2)}",
    )


def maybe_execute_backup(
    price: Decimal,
) -> None:

    if not STATE.is_open():

        return

    plan = pending_plan(
        "BACKUP"
    )

    if not plan:

        return

    if STATE.side == "LONG":

        triggered = (
            price
            <= plan.trigger_price
        )

    else:

        triggered = (
            price
            >= plan.trigger_price
        )

    if not triggered:

        return

    cancel_plans(
        "PYRAMID",
        "backup trigger reached",
    )

    ok, reason = (
        execute_simulated_add(
            "BACKUP",
            plan.slot,
            plan.allocation_percent,
            price,
        )
    )

    if ok:

        plan.status = (
            "FILLED"
        )

        plan.reason = (
            "backup trigger reached"
        )

        ensure_next_backup_plan(
            price
        )

    else:

        plan.status = (
            "CANCELLED"
        )

        plan.reason = (
            reason
        )

        print(
            f"BACKUP BLOCKED: "
            f"{reason}"
        )


def profit_percent_from_entry(
    price: Decimal,
) -> Decimal:

    if (
        not STATE.is_open()
        or STATE.entry_price <= 0
    ):

        return D0

    if STATE.side == "LONG":

        return (
            (
                price
                - STATE.entry_price
            )
            / STATE.entry_price
            * D100
        )

    return (
        (
            STATE.entry_price
            - price
        )
        / STATE.entry_price
        * D100
    )


def manage_take_profit(
    price: Decimal,
) -> None:

    if not STATE.is_open():

        return

    profit_percent = (
        profit_percent_from_entry(
            price
        )
    )

    if (
        not STATE.tp1_done
        and profit_percent
        >= TP1_PROFIT_PERCENT
    ):

        close_fraction(
            TP1_PERCENT_OF_POSITION,
            price,
            "TP1",
        )

        STATE.tp1_done = (
            True
        )

    if not STATE.is_open():

        return

    if (
        not STATE.tp2_done
        and profit_percent
        >= TP2_PROFIT_PERCENT
    ):

        close_fraction(
            TP2_PERCENT_OF_POSITION,
            price,
            "TP2",
        )

        STATE.tp2_done = (
            True
        )

        STATE.trailing_active = (
            True
        )

        STATE.trailing_peak = (
            price
        )

        STATE.trailing_trough = (
            price
        )

        cancel_plans(
            "PYRAMID",
            (
                "TP2 reached; "
                "TP3 trailing active"
            ),
        )

        cancel_plans(
            "BACKUP",
            (
                "TP2 reached; "
                "TP3 trailing active"
            ),
        )

        print(
            "TP3 TRAILING ACTIVATED",
            f"| distance="
            f"{fmt(TRAILING_DISTANCE_PERCENT, 2)}%",
        )

    if (
        not STATE.is_open()
        or not STATE.trailing_active
    ):

        return

    if STATE.side == "LONG":

        STATE.trailing_peak = (
            max(
                STATE.trailing_peak,
                price,
            )
        )

        stop_price = (
            STATE.trailing_peak
            * (
                Decimal("1")
                - pct(
                    TRAILING_DISTANCE_PERCENT
                )
            )
        )

        if price <= stop_price:

            close_entire_position(
                price,
                "TP3 trailing stop",
            )

    else:

        if (
            STATE.trailing_trough
            <= 0
        ):

            STATE.trailing_trough = (
                price
            )

        STATE.trailing_trough = (
            min(
                STATE.trailing_trough,
                price,
            )
        )

        stop_price = (
            STATE.trailing_trough
            * (
                Decimal("1")
                + pct(
                    TRAILING_DISTANCE_PERCENT
                )
            )
        )

        if price >= stop_price:

            close_entire_position(
                price,
                "TP3 trailing stop",
            )


def manage_safety_exit(
    price: Decimal,
    strong_trend_side: Optional[str],
) -> None:

    if not STATE.is_open():

        return

    loss_percent = (
        current_trade_loss_percent(
            STATE,
            price,
        )
    )

    if (
        loss_percent
        >= MAX_TRADE_LOSS_PERCENT
    ):

        cancel_plans(
            None,
            (
                "maximum trade "
                "loss reached"
            ),
        )

        close_entire_position(
            price,
            "maximum trade loss",
        )

        return

    if (
        TREND_REVERSAL_EXIT
        and strong_trend_side
        is not None
        and strong_trend_side
        != STATE.side
    ):

        cancel_plans(
            None,
            (
                "confirmed "
                "trend reversal"
            ),
        )

        close_entire_position(
            price,
            (
                "confirmed "
                "trend reversal"
            ),
        )


PREVIOUS_EMA_FAST: Optional[
    Decimal
] = None

PREVIOUS_EMA_MID: Optional[
    Decimal
] = None


PENDING_SIGNAL_SIDE: Optional[
    str
] = None

PENDING_SIGNAL_TIME = 0.0

PENDING_SIGNAL_CONFIRM_AFTER_CANDLE = 0

CLOSED_CANDLE_COUNTER = 0


def detect_crossover(
    previous_fast: Optional[Decimal],
    previous_mid: Optional[Decimal],
    current_fast: Decimal,
    current_mid: Decimal,
) -> Optional[str]:

    if (
        previous_fast is None
        or previous_mid is None
    ):

        return None

    if (
        previous_fast
        <= previous_mid
        and current_fast
        > current_mid
    ):

        return "LONG"

    if (
        previous_fast
        >= previous_mid
        and current_fast
        < current_mid
    ):

        return "SHORT"

    return None


def set_pending_signal(
    side: str,
) -> None:

    global PENDING_SIGNAL_SIDE

    global PENDING_SIGNAL_TIME

    global PENDING_SIGNAL_CONFIRM_AFTER_CANDLE

    PENDING_SIGNAL_SIDE = (
        side
    )

    PENDING_SIGNAL_TIME = (
        now_ts()
    )

    PENDING_SIGNAL_CONFIRM_AFTER_CANDLE = (
        CLOSED_CANDLE_COUNTER
        + 1
    )

    print(
        f"{side} CROSSOVER DETECTED"
    )

    print(
        "SIGNAL ENTERED PENDING STATE"
    )

    print(
        "WAITING FOR NEXT-CANDLE CONFIRMATION"
    )


def clear_pending_signal(
    reason: str,
) -> None:

    global PENDING_SIGNAL_SIDE

    global PENDING_SIGNAL_TIME

    global PENDING_SIGNAL_CONFIRM_AFTER_CANDLE

    if PENDING_SIGNAL_SIDE:

        print(
            "PENDING SIGNAL CLEARED:",
            reason,
        )

    PENDING_SIGNAL_SIDE = None

    PENDING_SIGNAL_TIME = 0.0

    PENDING_SIGNAL_CONFIRM_AFTER_CANDLE = 0


async def evaluate_pending_signal(
    price: Decimal,
    ema_fast: Decimal,
    ema_mid: Decimal,
    ema_slow: Decimal,
) -> None:

    if not PENDING_SIGNAL_SIDE:

        return

    age = (
        now_ts()
        - PENDING_SIGNAL_TIME
    )

    if (
        age
        > SIGNAL_EXPIRY_SECONDS
    ):

        clear_pending_signal(
            "signal expired"
        )

        return

    if (
        CLOSED_CANDLE_COUNTER
        < PENDING_SIGNAL_CONFIRM_AFTER_CANDLE
    ):

        return

    side = (
        PENDING_SIGNAL_SIDE
    )

    structure = (
        structure_label(
            ema_fast,
            ema_mid,
            ema_slow,
        )
    )

    strong_side = (
        direction_from_structure(
            structure
        )
    )

    separation = (
        ema_separation_percent(
            price,
            ema_fast,
            ema_mid,
        )
    )

    if strong_side != side:

        clear_pending_signal(
            (
                "confirmation failed: "
                f"structure={structure}"
            )
        )

        return

    if (
        separation
        < MIN_EMA_19_50_SEPARATION_PERCENT
    ):

        clear_pending_signal(
            (
                "quality filter failed: "
                "EMA separation "
                f"{fmt(separation, 4)}%"
            )
        )

        return

    if STATE.is_open():

        clear_pending_signal(
            "position already open"
        )

        return

    ok, reason = (
        open_simulated_position(
            side,
            price,
        )
    )

    if ok:

        await send_telegram(
            f"🧪 MODULE {MODULE_NAME}\n"
            f"{SYMBOL}\n"
            f"SIMULATED {side} ENTRY\n\n"
            f"Price: {fmt(price, 2)}\n"
            f"EMA{EMA_FAST}: {fmt(ema_fast, 2)}\n"
            f"EMA{EMA_MID}: {fmt(ema_mid, 2)}\n"
            f"EMA{EMA_SLOW}: {fmt(ema_slow, 2)}\n\n"
            f"Entry: {fmt(INITIAL_ENTRY_PERCENT, 2)}%\n"
            f"Leverage: {fmt(LEVERAGE, 2)}x\n\n"
            f"⚠️ Live execution disabled"
        )

        ensure_next_pyramid_plan(
            price,
            strong_side,
        )

        ensure_next_backup_plan(
            price
        )

    else:

        print(
            f"ENTRY BLOCKED: "
            f"{reason}"
        )

    clear_pending_signal(
        "processed"
    )


def extract_close_from_row(
    row: Any,
) -> Optional[Decimal]:

    try:

        if isinstance(
            row,
            (list, tuple),
        ):

            if len(row) > 4:

                value = d(
                    row[4],
                    Decimal("-1"),
                )

                if value > 0:

                    return value

        elif isinstance(
            row,
            dict,
        ):

            for key in (
                "close",
                "c",
                "closePrice",
                "lastPrice",
            ):

                if key in row:

                    value = d(
                        row[key],
                        Decimal("-1"),
                    )

                    if value > 0:

                        return value

    except Exception:

        pass

    return None


def extract_rows(
    payload: Any,
) -> list[Any]:

    if isinstance(
        payload,
        list,
    ):

        return payload

    if isinstance(
        payload,
        dict,
    ):

        for key in (
            "data",
            "result",
            "rows",
            "list",
        ):

            value = payload.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return value

            if isinstance(
                value,
                dict,
            ):

                for nested in (
                    "list",
                    "rows",
                    "data",
                ):

                    nested_value = (
                        value.get(
                            nested
                        )
                    )

                    if isinstance(
                        nested_value,
                        list,
                    ):

                        return nested_value

    return []


async def load_historical_closes(
    session: aiohttp.ClientSession,
) -> list[Decimal]:

    print(
        "LOADING 1m HISTORICAL CANDLES..."
    )

    parameter_sets = [

        {
            "symbol": SYMBOL,
            "interval": "1m",
            "limit": str(
                HISTORICAL_LIMIT
            ),
        },

        {
            "symbol": SYMBOL,
            "period": "1m",
            "limit": str(
                HISTORICAL_LIMIT
            ),
        },

    ]

    for params in parameter_sets:

        try:

            async with session.get(
                HISTORICAL_URL,
                params=params,
                timeout=(
                    aiohttp.ClientTimeout(
                        total=15
                    )
                ),
                headers={
                    "User-Agent":
                    f"WEEX-{MODULE_NAME}/1.0"
                },
            ) as response:

                print(
                    "HISTORICAL HTTP STATUS:",
                    response.status,
                )

                if (
                    response.status
                    != 200
                ):

                    continue

                payload = (
                    await response.json(
                        content_type=None
                    )
                )

                rows = (
                    extract_rows(
                        payload
                    )
                )

                closes = []

                for row in rows:

                    close = (
                        extract_close_from_row(
                            row
                        )
                    )

                    if close is not None:

                        closes.append(
                            close
                        )

                if (
                    len(closes)
                    >= EMA_SLOW
                ):

                    try:

                        if (
                            len(rows) >= 2
                            and isinstance(
                                rows[0],
                                (list, tuple),
                            )
                            and isinstance(
                                rows[1],
                                (list, tuple),
                            )
                            and d(
                                rows[0][0]
                            )
                            > d(
                                rows[1][0]
                            )
                        ):

                            closes.reverse()

                    except Exception:

                        pass

                    print(
                        "HISTORICAL CANDLES LOADED:",
                        len(closes),
                    )

                    print(
                        "LATEST CLOSED PRICE:",
                        fmt(
                            closes[-1],
                            2,
                        ),
                    )

                    return closes[
                        -HISTORICAL_LIMIT:
                    ]

        except Exception as exc:

            print(
                "HISTORICAL ERROR:",
                type(exc).__name__,
                exc,
            )

    return []


def walk_for_candle_candidates(
    obj: Any,
) -> list[
    dict[str, Any]
]:

    found = []

    if isinstance(
        obj,
        dict,
    ):

        keys = set(
            obj.keys()
        )

        interesting = {

            "close",

            "c",

            "closePrice",

            "lastPrice",

            "timestamp",

            "ts",

            "time",

            "startTime",

            "confirm",

            "closed",

            "isClosed",

        }

        if keys & interesting:

            found.append(
                obj
            )

        for value in obj.values():

            found.extend(
                walk_for_candle_candidates(
                    value
                )
            )

    elif isinstance(
        obj,
        list,
    ):

        for item in obj:

            found.extend(
                walk_for_candle_candidates(
                    item
                )
            )

    return found


def extract_live_close(
    message: Any,
):

    candidates = (
        walk_for_candle_candidates(
            message
        )
    )

    for item in candidates:

        close = None

        for key in (
            "close",
            "c",
            "closePrice",
            "lastPrice",
            "price",
        ):

            if key in item:

                value = d(
                    item[key],
                    Decimal("-1"),
                )

                if value > 0:

                    close = value

                    break

        if close is None:

            continue

        closed = None

        for key in (
            "confirm",
            "closed",
            "isClosed",
        ):

            if key in item:

                raw = item[key]

                if isinstance(
                    raw,
                    bool,
                ):

                    closed = raw

                elif str(
                    raw
                ).lower() in {
                    "true",
                    "1",
                    "yes",
                }:

                    closed = True

                elif str(
                    raw
                ).lower() in {
                    "false",
                    "0",
                    "no",
                }:

                    closed = False

                break

        candle_ts = None

        for key in (
            "timestamp",
            "ts",
            "time",
            "startTime",
        ):

            if key in item:

                try:

                    candle_ts = int(
                        float(
                            item[key]
                        )
                    )

                    if (
                        candle_ts
                        > 10**12
                    ):

                        candle_ts //= (
                            1000
                        )

                except Exception:

                    candle_ts = None

                break

        return (
            close,
            closed,
            candle_ts,
        )

    data = (
        message.get("data")
        if isinstance(
            message,
            dict,
        )
        else None
    )

    if isinstance(
        data,
        list,
    ):

        for row in data:

            if (
                isinstance(
                    row,
                    (list, tuple),
                )
                and len(row) >= 5
            ):

                close = d(
                    row[4],
                    Decimal("-1"),
                )

                if close > 0:

                    try:

                        candle_ts = int(
                            float(
                                row[0]
                            )
                        )

                        if (
                            candle_ts
                            > 10**12
                        ):

                            candle_ts //= (
                                1000
                            )

                    except Exception:

                        candle_ts = None

                    return (
                        close,
                        None,
                        candle_ts,
                    )

    return (
        None,
        None,
        None,
    )


LAST_PROCESSED_CANDLE_TS: Optional[
    int
] = None


async def process_closed_candle(
    closes: list[Decimal],
    close_price: Decimal,
    candle_ts: Optional[int],
) -> None:

    global PREVIOUS_EMA_FAST

    global PREVIOUS_EMA_MID

    global CLOSED_CANDLE_COUNTER

    global LAST_PROCESSED_CANDLE_TS

    if (
        candle_ts is not None
        and candle_ts
        == LAST_PROCESSED_CANDLE_TS
    ):

        return

    LAST_PROCESSED_CANDLE_TS = (
        candle_ts
    )

    CLOSED_CANDLE_COUNTER += 1

    closes.append(
        close_price
    )

    if (
        len(closes)
        > HISTORICAL_LIMIT
    ):

        del closes[
            :-HISTORICAL_LIMIT
        ]

    (
        ema_fast,
        ema_mid,
        ema_slow,
    ) = calculate_emas(
        closes
    )

    if (
        ema_fast is None
        or ema_mid is None
        or ema_slow is None
    ):

        return

    structure = (
        structure_label(
            ema_fast,
            ema_mid,
            ema_slow,
        )
    )

    strong_side = (
        direction_from_structure(
            structure
        )
    )

    log_bar()

    print(
        f"{MODULE_NAME} CLOSED 1m CANDLE"
    )

    print(
        f"{SYMBOL} CLOSE: "
        f"{fmt(close_price, 2)}"
    )

    print(
        f"EMA{EMA_FAST}: "
        f"{fmt(ema_fast, 2)}"
    )

    print(
        f"EMA{EMA_MID}: "
        f"{fmt(ema_mid, 2)}"
    )

    print(
        f"EMA{EMA_SLOW}: "
        f"{fmt(ema_slow, 2)}"
    )

    print(
        f"STRUCTURE: {structure}"
    )

    if STATE.is_open():

        print(
            f"POSITION: "
            f"{STATE.side}"
        )

        print(
            f"AVG ENTRY: "
            f"{fmt(STATE.entry_price, 2)}"
        )

        print(
            f"EST LIQ: "
            f"{fmt(STATE.estimated_liquidation_price, 2)}"
        )

        print(
            "PYRAMIDS FILLED:",
            (
                f"{STATE.pyramid_adds_filled}"
                f"/{MAX_PYRAMID_ADDS}"
            ),
        )

        print(
            "BACKUPS FILLED:",
            (
                f"{STATE.backups_filled}"
                f"/{MAX_BACKUPS}"
            ),
        )

        print(
            "FUND EXPOSURE:",
            (
                f"{fmt(fund_exposure_percent(STATE.margin_used), 2)}%"
            ),
        )

        print(
            "UNREALIZED PNL:",
            (
                f"{fmt(unrealized_pnl(STATE, close_price), 4)} USDT"
            ),
        )

    crossover = (
        detect_crossover(
            PREVIOUS_EMA_FAST,
            PREVIOUS_EMA_MID,
            ema_fast,
            ema_mid,
        )
    )

    if crossover is not None:

        set_pending_signal(
            crossover
        )

    PREVIOUS_EMA_FAST = (
        ema_fast
    )

    PREVIOUS_EMA_MID = (
        ema_mid
    )

    manage_safety_exit(
        close_price,
        strong_side,
    )

    if STATE.is_open():

        cleanup_expired_idle_pyramids(
            now_ts()
        )

        ensure_next_pyramid_plan(
            close_price,
            strong_side,
        )

        maybe_execute_pyramid(
            close_price,
            strong_side,
        )

        ensure_next_backup_plan(
            close_price
        )

        maybe_execute_backup(
            close_price
        )

        manage_take_profit(
            close_price
        )

    await evaluate_pending_signal(
        close_price,
        ema_fast,
        ema_mid,
        ema_slow,
    )

    prune_finished_plans()

    log_bar()


async def websocket_loop(
    closes: list[Decimal],
) -> None:

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    live_candle_timestamp = (
        None
    )

    live_candle_close = (
        None
    )

    while True:

        try:

            async with websockets.connect(
                WS_URL,
                ping_interval=None,
                close_timeout=10,
                additional_headers={
                    "User-Agent":
                    f"WEEX-{MODULE_NAME}/1.0"
                },
            ) as ws:

                print(
                    "CONNECTED TO WEEX"
                )

                subscribe_payload = {

                    "method":
                    "SUBSCRIBE",

                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],

                    "id":
                    1,

                }

                await ws.send(
                    json.dumps(
                        subscribe_payload
                    )
                )

                print(
                    "SUBSCRIBED TO",
                    SUBSCRIPTION_CHANNEL,
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                async for raw in ws:

                    if raw is None:

                        continue

                    if isinstance(
                        raw,
                        bytes,
                    ):

                        raw = raw.decode(
                            "utf-8",
                            errors="ignore",
                        )

                    if (
                        raw.strip().lower()
                        == "ping"
                    ):

                        await ws.send(
                            "pong"
                        )

                        continue

                    try:

                        message = (
                            json.loads(
                                raw
                            )
                        )

                    except json.JSONDecodeError:

                        continue

                    if isinstance(
                        message,
                        dict,
                    ):

                        if (
                            message.get("event")
                            == "ping"
                        ):

                            pong = {

                                "event":
                                "pong",

                                "ts":
                                message.get(
                                    "ts"
                                ),

                            }

                            await ws.send(
                                json.dumps(
                                    pong
                                )
                            )

                            continue

                        if (
                            message.get("id")
                            == 1
                            or message.get(
                                "event"
                            )
                            in {
                                "subscribe",
                                "subscribed",
                            }
                        ):

                            print(
                                "SUBSCRIPTION CONFIRMED"
                            )

                    (
                        close_price,
                        explicit_closed,
                        candle_ts,
                    ) = extract_live_close(
                        message
                    )

                    if (
                        close_price is None
                        or close_price <= 0
                    ):

                        continue

                    if (
                        explicit_closed
                        is True
                    ):

                        await process_closed_candle(
                            closes,
                            close_price,
                            candle_ts,
                        )

                        live_candle_timestamp = (
                            candle_ts
                        )

                        live_candle_close = (
                            close_price
                        )

                        continue

                    if (
                        candle_ts
                        is not None
                    ):

                        minute_ts = (
                            candle_ts
                            - (
                                candle_ts
                                % 60
                            )
                        )

                        if (
                            live_candle_timestamp
                            is None
                        ):

                            live_candle_timestamp = (
                                minute_ts
                            )

                            live_candle_close = (
                                close_price
                            )

                            print(
                                "LIVE 1m CANDLE STARTED:",
                                fmt(
                                    close_price,
                                    2,
                                ),
                            )

                            continue

                        if (
                            minute_ts
                            == live_candle_timestamp
                        ):

                            live_candle_close = (
                                close_price
                            )

                            continue

                        if (
                            minute_ts
                            > live_candle_timestamp
                        ):

                            if (
                                live_candle_close
                                is not None
                            ):

                                await process_closed_candle(
                                    closes,
                                    live_candle_close,
                                    live_candle_timestamp,
                                )

                            live_candle_timestamp = (
                                minute_ts
                            )

                            live_candle_close = (
                                close_price
                            )

                            print(
                                "NEW LIVE 1m CANDLE:",
                                fmt(
                                    close_price,
                                    2,
                                ),
                            )

                            continue

        except asyncio.CancelledError:

            raise

        except Exception as exc:

            print(
                "WEBSOCKET ERROR:",
                type(exc).__name__,
                exc,
            )

            print(
                "RECONNECTING IN",
                reconnect_delay,
                "SECONDS...",
            )

            await asyncio.sleep(
                reconnect_delay
            )

            reconnect_delay = min(
                reconnect_delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


def validate_configuration() -> None:

    errors = []

    if (
        INITIAL_ENTRY_PERCENT
        <= 0
    ):

        errors.append(
            (
                "INITIAL_ENTRY_PERCENT "
                "must be > 0"
            )
        )

    if LEVERAGE <= 0:

        errors.append(
            "LEVERAGE must be > 0"
        )

    if (
        LEVERAGE
        > MAX_LEVERAGE
    ):

        errors.append(
            (
                "LEVERAGE cannot exceed "
                "MAX_LEVERAGE"
            )
        )

    if (
        MAX_PYRAMID_ADDS
        > len(
            PYRAMID_PERCENTS
        )
    ):

        errors.append(
            (
                "MAX_PYRAMID_ADDS cannot "
                "exceed 3 in this build"
            )
        )

    if (
        MAX_BACKUPS
        > len(
            BACKUP_PERCENTS
        )
    ):

        errors.append(
            (
                "MAX_BACKUPS cannot "
                "exceed 3 in this build"
            )
        )

    total_tp = (
        TP1_PERCENT_OF_POSITION
        + TP2_PERCENT_OF_POSITION
        + TP3_PERCENT_OF_POSITION
    )

    if total_tp != D100:

        errors.append(
            (
                "TP1 + TP2 + TP3 position "
                "percentages must equal 100"
            )
        )

    if (
        MAX_FUND_EXPOSURE_PERCENT
        <= 0
        or MAX_FUND_EXPOSURE_PERCENT
        > 100
    ):

        errors.append(
            (
                "MAX_FUND_EXPOSURE_PERCENT "
                "must be between 0 and 100"
            )
        )

    if (
        SIMULATED_ACCOUNT_EQUITY_USDT
        <= 0
    ):

        errors.append(
            (
                "SIMULATED_ACCOUNT_EQUITY_USDT "
                "must be > 0"
            )
        )

    if LIVE_ORDER_EXECUTION:

        errors.append(
            (
                "LIVE_ORDER_EXECUTION must "
                "remain False in 0F-4B"
            )
        )

    if errors:

        for error in errors:

            print(
                "CONFIG ERROR:",
                error,
            )

        raise RuntimeError(
            (
                "Invalid 0F-4B "
                "configuration"
            )
        )


def print_startup_banner() -> None:

    log_bar()

    print(
        f"MODULE {MODULE_NAME} STARTING"
    )

    print(
        (
            f"{SYMBOL} POSITION + "
            "LIQUIDATION/BACKUP "
            "PLANNING ENGINE"
        )
    )

    print(
        (
            f"EMA{EMA_FAST} / "
            f"EMA{EMA_MID} / "
            f"EMA{EMA_SLOW}"
        )
    )

    print(
        "IDLE PYRAMID CLEANUP ENABLED"
    )

    log_bar()

    print(
        "TRADE CONFIGURATION"
    )

    print(
        "SIMULATED EQUITY:",
        (
            f"{fmt(SIMULATED_ACCOUNT_EQUITY_USDT, 2)} "
            "USDT"
        ),
    )

    print(
        "INITIAL ENTRY:",
        f"{fmt(INITIAL_ENTRY_PERCENT, 2)}%",
    )

    print(
        "LEVERAGE:",
        f"{fmt(LEVERAGE, 2)}x",
    )

    print(
        "MAX LEVERAGE:",
        f"{fmt(MAX_LEVERAGE, 2)}x",
    )

    print(
        "MAX PYRAMIDS:",
        MAX_PYRAMID_ADDS,
    )

    print(
        "PYRAMID TRIGGER:",
        (
            f"{fmt(PYRAMID_TRIGGER_PERCENT, 2)}% "
            "favorable"
        ),
    )

    print(
        "PYRAMID EXPIRY:",
        f"{PYRAMID_EXPIRY_SECONDS}s",
    )

    print(
        "MAX BACKUPS:",
        MAX_BACKUPS,
    )

    print(
        "BACKUP LIQ BUFFER:",
        (
            f"{fmt(BACKUP_LIQUIDATION_BUFFER_PERCENT, 2)}%"
        ),
    )

    print(
        "MIN LIQ DISTANCE:",
        (
            f"{fmt(MIN_LIQUIDATION_DISTANCE_PERCENT, 2)}%"
        ),
    )

    print(
        "MAX FUND EXPOSURE:",
        (
            f"{fmt(MAX_FUND_EXPOSURE_PERCENT, 2)}%"
        ),
    )

    print(
        "MAX TOTAL LEVERAGE EXPOSURE:",
        (
            f"{fmt(MAX_TOTAL_LEVERAGE_EXPOSURE, 2)}x"
        ),
    )

    print(
        "MAX TRADE LOSS:",
        (
            f"{fmt(MAX_TRADE_LOSS_PERCENT, 2)}%"
        ),
    )

    print(
        "TP1 / TP2 / TP3:",
        (
            f"{fmt(TP1_PERCENT_OF_POSITION, 0)}% / "
            f"{fmt(TP2_PERCENT_OF_POSITION, 0)}% / "
            f"{fmt(TP3_PERCENT_OF_POSITION, 0)}%"
        ),
    )

    print(
        "ONE DIRECTION ONLY:",
        (
            "ON"
            if ONE_DIRECTION_ONLY
            else "OFF"
        ),
    )

    print(
        "ANTI DUPLICATE:",
        (
            "ON"
            if ANTI_DUPLICATE_ORDERS
            else "OFF"
        ),
    )

    print(
        "TREND REVERSAL EXIT:",
        (
            "ON"
            if TREND_REVERSAL_EXIT
            else "OFF"
        ),
    )

    print(
        "TELEGRAM CONFIG:",
        (
            "READY"
            if telegram_is_configured()
            else "MISSING"
        ),
    )

    print(
        "LIVE ORDER EXECUTION: DISABLED"
    )

    print(
        (
            "LIQUIDATION PRICE: "
            "LOCAL SIMULATION ESTIMATE ONLY"
        )
    )

    log_bar()


async def main() -> None:

    validate_configuration()

    print_startup_banner()

    connector = (
        aiohttp.TCPConnector(
            limit=20
        )
    )

    async with aiohttp.ClientSession(
        connector=connector
    ) as session:

        closes = (
            await load_historical_closes(
                session
            )
        )

        if (
            len(closes)
            < EMA_SLOW
        ):

            print(
                (
                    "ERROR: NOT ENOUGH "
                    "HISTORICAL CANDLES "
                    f"FOR EMA{EMA_SLOW}"
                )
            )

            return

        (
            ema_fast,
            ema_mid,
            ema_slow,
        ) = calculate_emas(
            closes
        )

        if (
            ema_fast is None
            or ema_mid is None
            or ema_slow is None
        ):

            print(
                (
                    "ERROR: EMA ENGINE "
                    "COULD NOT INITIALIZE"
                )
            )

            return

        global PREVIOUS_EMA_FAST

        global PREVIOUS_EMA_MID

        PREVIOUS_EMA_FAST = (
            ema_fast
        )

        PREVIOUS_EMA_MID = (
            ema_mid
        )

        print(
            "INITIAL EMA ENGINE"
        )

        print(
            f"EMA{EMA_FAST}: "
            f"{fmt(ema_fast, 2)}"
        )

        print(
            f"EMA{EMA_MID}: "
            f"{fmt(ema_mid, 2)}"
        )

        print(
            f"EMA{EMA_SLOW}: "
            f"{fmt(ema_slow, 2)}"
        )

        print(
            "STRUCTURE:",
            structure_label(
                ema_fast,
                ema_mid,
                ema_slow,
            ),
        )

        print(
            "EMA ENGINE READY"
        )

        log_bar()

        await send_telegram(
            f"✅ MODULE {MODULE_NAME} ONLINE\n"
            f"{SYMBOL}\n"
            f"Position + Liquidation/Backup Planning Engine\n"
            f"EMA{EMA_FAST} / EMA{EMA_MID} / EMA{EMA_SLOW}\n"
            f"Initial Entry: {fmt(INITIAL_ENTRY_PERCENT, 2)}%\n"
            f"Leverage: {fmt(LEVERAGE, 2)}x\n"
            f"Max Pyramids: {MAX_PYRAMID_ADDS}\n"
            f"Max Backups: {MAX_BACKUPS}\n"
            f"Idle pyramid cleanup: ACTIVE\n"
            f"🛡 Safety controls active\n"
            f"⚠️ Live order execution disabled"
        )

        print(
            "LIVE SIGNAL MODE ACTIVE"
        )

        print(
            "POSITION PLANNING ACTIVE"
        )

        print(
            (
                "SEQUENTIAL BACKUP "
                "RECALCULATION ACTIVE"
            )
        )

        print(
            "IDLE PYRAMID CLEANUP ACTIVE"
        )

        print(
            "SIMULATED EXECUTION ONLY"
        )

        log_bar()

        await websocket_loop(
            closes
        )


if __name__ == "__main__":

    asyncio.run(
        main())
