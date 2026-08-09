import os, time, asyncio
from dataclasses import dataclass, field
from decimal import Decimal as D
from telegram import Bot


# ============================================================
# MODULE 0F-4C
# ============================================================

MODULE = "0F-4C"

SYMBOL = os.getenv("SYMBOL", "BTCUSDT")

LIVE_ORDERS = (
    os.getenv("LIVE_ORDERS", "false").lower()
    == "true"
)

TG_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

TG_CHAT = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
).strip()


# ============================================================
# HELPERS
# ============================================================

def envd(name, default):
    return D(os.getenv(name, str(default)))


def envi(name, default):
    return int(os.getenv(name, str(default)))


def envb(name, default):
    return os.getenv(
        name,
        str(default)
    ).lower() in (
        "1", "true", "yes", "on"
    )


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(maximum, value)
    )


# ============================================================
# TRADE CONFIGURATION
# ============================================================

ENTRY_PCT = envd(
    "INITIAL_ENTRY_PCT",
    5
)

LEVERAGE = envd(
    "LEVERAGE",
    5
)

MAX_LEVERAGE = envd(
    "MAX_LEVERAGE",
    10
)


# ============================================================
# PYRAMID CONFIGURATION
# ============================================================

MAX_PYRAMIDS = envi(
    "MAX_PYRAMIDS",
    1
)

PYRAMID_PCTS = [
    D(x)
    for x in os.getenv(
        "PYRAMID_PCTS",
        "2.5"
    ).split(",")
    if x.strip()
]

PYRAMID_TRIGGER = envd(
    "PYRAMID_TRIGGER_PCT",
    0.35
)

IDLE_PYRAMID_CLEANUP_SEC = envi(
    "IDLE_PYRAMID_CLEANUP_SEC",
    180
)


# ============================================================
# BACKUP CONFIGURATION
# ============================================================

MAX_BACKUPS = envi(
    "MAX_BACKUPS",
    3
)

BACKUP_PCTS = [
    D(x)
    for x in os.getenv(
        "BACKUP_PCTS",
        "5,7.5,10"
    ).split(",")
    if x.strip()
]

BACKUP_BUFFER_PCT = envd(
    "BACKUP_LIQ_BUFFER_PCT",
    0.35
)

MIN_LIQ_DISTANCE_PCT = envd(
    "MIN_LIQ_DISTANCE_PCT",
    1
)


# ============================================================
# PROFIT MANAGEMENT
# ============================================================

TP1_PCT = envd(
    "TP1_POSITION_PCT",
    20
)

TP2_PCT = envd(
    "TP2_POSITION_PCT",
    20
)

TP3_PCT = envd(
    "TP3_POSITION_PCT",
    60
)

TP1_TRIGGER = envd(
    "TP1_TRIGGER_PCT",
    0.50
)

TP2_TRIGGER = envd(
    "TP2_TRIGGER_PCT",
    1.00
)

TRAIL_DISTANCE = envd(
    "TRAIL_DISTANCE_PCT",
    0.20
)


# ============================================================
# SAFETY CONTROLS
# ============================================================

MAX_FUND_EXPOSURE_PCT = envd(
    "MAX_FUND_EXPOSURE_PCT",
    35
)

MAX_TRADE_LOSS_PCT = envd(
    "MAX_TRADE_LOSS_PCT",
    8
)

SIGNAL_EXPIRY_SEC = envi(
    "SIGNAL_EXPIRY_SEC",
    180
)

COOLDOWN_SEC = envi(
    "LOSS_COOLDOWN_SEC",
    300
)

ONE_DIRECTION_ONLY = envb(
    "ONE_DIRECTION_ONLY",
    True
)

ANTI_DUPLICATE = envb(
    "ANTI_DUPLICATE_ORDERS",
    True
)

TREND_REVERSAL_EXIT = envb(
    "TREND_REVERSAL_EXIT",
    True
)


# ============================================================
# TRADE STATE
# ============================================================

@dataclass
class Trade:

    side: str
    entry: D
    equity: D

    opened: float = field(
        default_factory=time.time
    )

    qty_pct: D = ENTRY_PCT

    avg: D = D("0")

    pyramids: int = 0
    backups: int = 0

    tp1: bool = False
    tp2: bool = False

    trailing: bool = False

    peak: D = D("0")
    trough: D = D("0")

    last_action: str = "ENTRY"

    pending_pyramids: list = field(
        default_factory=list
    )

    def __post_init__(self):

        self.side = self.side.upper()

        self.avg = self.entry

        self.peak = self.entry
        self.trough = self.entry


    # --------------------------------------------------------
    # PROFIT / LOSS
    # --------------------------------------------------------

    def pnl_pct(self, price):

        movement = (
            price / self.avg - 1
        ) * 100

        if self.side == "LONG":
            return movement

        return -movement


    # --------------------------------------------------------
    # ESTIMATED LIQUIDATION
    # --------------------------------------------------------

    def est_liq(self):

        leverage = clamp(
            LEVERAGE,
            D("1"),
            MAX_LEVERAGE
        )

        movement = (
            D("100")
            / leverage
        )

        if self.side == "LONG":

            return self.avg * (
                1 - movement / 100
            )

        return self.avg * (
            1 + movement / 100
        )


    # --------------------------------------------------------
    # NEXT BACKUP PRICE
    # --------------------------------------------------------

    def next_backup_price(self):

        liquidation = self.est_liq()

        buffer = (
            BACKUP_BUFFER_PCT
            / 100
        )

        if self.side == "LONG":

            return liquidation * (
                1 + buffer
            )

        return liquidation * (
            1 - buffer
        )


    # --------------------------------------------------------
    # ADD POSITION
    # --------------------------------------------------------

    def add(self, price, pct, kind):

        available = (
            MAX_FUND_EXPOSURE_PCT
            - self.qty_pct
        )

        pct = min(
            pct,
            available
        )

        if pct <= 0:
            return False

        self.avg = (
            self.avg * self.qty_pct
            + price * pct
        ) / (
            self.qty_pct + pct
        )

        self.qty_pct += pct

        self.last_action = kind

        return True


    # --------------------------------------------------------
    # REDUCE POSITION
    # --------------------------------------------------------

    def reduce(self, pct, label):

        amount = min(
            self.qty_pct,
            pct
        )

        self.qty_pct -= amount

        self.last_action = (
            f"{label} -{amount}%"
        )

        return amount


# ============================================================
# CONFIG VALIDATION
# ============================================================

def validate():

    if LEVERAGE > MAX_LEVERAGE:

        raise ValueError(
            "LEVERAGE exceeds MAX_LEVERAGE"
        )

    if (
        TP1_PCT
        + TP2_PCT
        + TP3_PCT
        != 100
    ):

        raise ValueError(
            "TP1 + TP2 + TP3 must equal 100%"
        )

    if (
        ENTRY_PCT
        > MAX_FUND_EXPOSURE_PCT
    ):

        raise ValueError(
            "INITIAL_ENTRY_PCT exceeds "
            "MAX_FUND_EXPOSURE_PCT"
        )


# ============================================================
# SIGNAL SAFETY
# ============================================================

def signal_ok(
    side,
    signal_time,
    active_side=None,
    last_signal=None
):

    if (
        time.time()
        - signal_time
        > SIGNAL_EXPIRY_SEC
    ):

        return False, "signal expired"

    if (
        ONE_DIRECTION_ONLY
        and active_side
        and active_side != side
    ):

        return (
            False,
            "opposite position active"
        )

    if (
        ANTI_DUPLICATE
        and last_signal == side
    ):

        return (
            False,
            "duplicate signal"
        )

    return True, "ok"


# ============================================================
# TRADE MANAGEMENT ENGINE
# ============================================================

def manage(
    trade,
    price,
    trend_side=None
):

    price = D(str(price))

    actions = []

    pnl = trade.pnl_pct(price)

    trade.peak = max(
        trade.peak,
        price
    )

    trade.trough = min(
        trade.trough,
        price
    )


    # ========================================================
    # TREND REVERSAL EXIT
    # ========================================================

    if (
        TREND_REVERSAL_EXIT
        and trend_side
        and trend_side != trade.side
    ):

        actions.append(
            (
                "EXIT",
                trade.qty_pct,
                price,
                "trend reversal"
            )
        )

        trade.qty_pct = D("0")

        return actions


    # ========================================================
    # MAXIMUM TRADE LOSS
    # ========================================================

    if pnl <= -MAX_TRADE_LOSS_PCT:

        actions.append(
            (
                "EXIT",
                trade.qty_pct,
                price,
                "max trade loss"
            )
        )

        trade.qty_pct = D("0")

        return actions


    # ========================================================
    # SEQUENTIAL BACKUP
    # ========================================================

    if trade.backups < MAX_BACKUPS:

        target = (
            trade.next_backup_price()
        )

        if trade.side == "LONG":

            backup_triggered = (
                price <= target
            )

        else:

            backup_triggered = (
                price >= target
            )

        if backup_triggered:

            index = min(
                trade.backups,
                len(BACKUP_PCTS) - 1
            )

            pct = BACKUP_PCTS[index]

            if trade.add(
                price,
                pct,
                f"BACKUP-{trade.backups + 1}"
            ):

                trade.backups += 1

                actions.append(
                    (
                        "BACKUP",
                        pct,
                        price,
                        f"backup {trade.backups}"
                    )
                )


    # ========================================================
    # PYRAMIDING
    # ========================================================

    while (
        trade.pyramids
        < MAX_PYRAMIDS
        and pnl
        >= PYRAMID_TRIGGER
        * (trade.pyramids + 1)
    ):

        index = min(
            trade.pyramids,
            len(PYRAMID_PCTS) - 1
        )

        pct = PYRAMID_PCTS[index]

        if not trade.add(
            price,
            pct,
            f"PYRAMID-{trade.pyramids + 1}"
        ):

            break

        trade.pyramids += 1

        actions.append(
            (
                "PYRAMID",
                pct,
                price,
                f"pyramid {trade.pyramids}"
            )
        )


    # ========================================================
    # TP1
    # ========================================================

    if (
        not trade.tp1
        and pnl >= TP1_TRIGGER
    ):

        amount = (
            trade.qty_pct
            * TP1_PCT
            / 100
        )

        trade.reduce(
            amount,
            "TP1"
        )

        trade.tp1 = True

        actions.append(
            (
                "TP1",
                amount,
                price,
                "20% partial profit"
            )
        )


    # ========================================================
    # TP2
    # ========================================================

    if (
        not trade.tp2
        and pnl >= TP2_TRIGGER
    ):

        amount = (
            trade.qty_pct
            * TP2_PCT
            / (
                D("100")
                - TP1_PCT
            )
        )

        trade.reduce(
            amount,
            "TP2"
        )

        trade.tp2 = True

        # TP3 starts trailing immediately
        trade.trailing = True

        actions.append(
            (
                "TP2",
                amount,
                price,
                "TP3 trailing activated"
            )
        )


    # ========================================================
    # TP3 TRAILING PROFIT
    # ========================================================

    if (
        trade.trailing
        and trade.qty_pct > 0
    ):

        if trade.side == "LONG":

            trailing_stop = (
                trade.peak
                * (
                    1
                    - TRAIL_DISTANCE
                    / 100
                )
            )

            trailing_hit = (
                price
                <= trailing_stop
            )

        else:

            trailing_stop = (
                trade.trough
                * (
                    1
                    + TRAIL_DISTANCE
                    / 100
                )
            )

            trailing_hit = (
                price
                >= trailing_stop
            )


        if trailing_hit:

            amount = trade.qty_pct

            trade.qty_pct = D("0")

            actions.append(
                (
                    "TRAIL-EXIT",
                    amount,
                    price,
                    f"stop {trailing_stop:.2f}"
                )
            )


    # ========================================================
    # IDLE PYRAMID CLEANUP
    # ========================================================

    if (
        trade.pending_pyramids
        and
        time.time()
        - trade.opened
        >= IDLE_PYRAMID_CLEANUP_SEC
    ):

        count = len(
            trade.pending_pyramids
        )

        trade.pending_pyramids.clear()

        actions.append(
            (
                "CLEANUP",
                D(count),
                price,
                "idle pyramids removed"
            )
        )


    return actions


# ============================================================
# TELEGRAM
# ============================================================

async def notify(text):

    if not (
        TG_TOKEN
        and TG_CHAT
    ):

        return

    try:

        await Bot(
            TG_TOKEN
        ).send_message(
            chat_id=TG_CHAT,
            text=text
        )

    except Exception as error:

        print(
            "TELEGRAM ERROR:",
            error
        )


# ============================================================
# STARTUP
# ============================================================

def startup():

    validate()

    print("=" * 60)

    print(
        f"MODULE {MODULE} STARTING"
    )

    print(
        f"{SYMBOL} PYRAMID + TP + "
        "TRAILING MANAGEMENT ENGINE"
    )

    print("=" * 60)

    print(
        f"Entry: {ENTRY_PCT}%"
    )

    print(
        f"Leverage: {LEVERAGE}x"
    )

    print(
        f"Max Leverage: "
        f"{MAX_LEVERAGE}x"
    )

    print(
        f"Max Pyramids: "
        f"{MAX_PYRAMIDS}"
    )

    print(
        f"Max Backups: "
        f"{MAX_BACKUPS}"
    )

    print(
        f"Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PCT}%"
    )

    print(
        f"TP1 / TP2 / TP3: "
        f"{TP1_PCT}% / "
        f"{TP2_PCT}% / "
        f"{TP3_PCT}%"
    )

    print(
        f"TP1 Trigger: "
        f"{TP1_TRIGGER}%"
    )

    print(
        f"TP2 Trigger: "
        f"{TP2_TRIGGER}%"
    )

    print(
        f"Trailing Distance: "
        f"{TRAIL_DISTANCE}%"
    )

    print(
        "Idle pyramid cleanup: "
        "ACTIVE"
    )

    print(
        "Safety controls: ACTIVE"
    )

    print(
        "LIVE ORDER EXECUTION:",
        "ENABLED"
        if LIVE_ORDERS
        else "DISABLED"
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    startup()

    asyncio.run(
        notify(
            f"✅ MODULE {MODULE} ONLINE\n"
            f"{SYMBOL}\n"
            "Pyramid + TP + Trailing "
            "Management Engine\n"
            "TP1 / TP2 / TP3: "
            f"{TP1_PCT}% / "
            f"{TP2_PCT}% / "
            f"{TP3_PCT}%\n"
            f"Max Pyramids: {MAX_PYRAMIDS}\n"
            f"Max Backups: {MAX_BACKUPS}\n"
            "🛡 Safety controls active\n"
            "⚠️ Live order execution "
            + (
                "ENABLED"
                if LIVE_ORDERS
                else "disabled"
            )
        
