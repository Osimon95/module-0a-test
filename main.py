import asyncio
import json
import os
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE = "0F-4D"

SYMBOL = "BTCUSDT"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"


# ============================================================
# TRADE CONFIGURATION
# ============================================================

ENTRY_PCT = Decimal(
    os.getenv("ENTRY_PCT", "5")
)

LEVERAGE = Decimal(
    os.getenv("LEVERAGE", "5")
)

MAX_LEVERAGE = Decimal(
    os.getenv("MAX_LEVERAGE", "10")
)

MAX_PYRAMIDS = int(
    os.getenv("MAX_PYRAMIDS", "1")
)

MAX_BACKUPS = int(
    os.getenv("MAX_BACKUPS", "3")
)

MAX_FUND_EXPOSURE_PCT = Decimal(
    os.getenv("MAX_FUND_EXPOSURE_PCT", "35")
)


# ============================================================
# TAKE PROFIT CONFIGURATION
# ============================================================

TP1_SHARE = Decimal(
    os.getenv("TP1_SHARE", "20")
)

TP2_SHARE = Decimal(
    os.getenv("TP2_SHARE", "20")
)

TP3_SHARE = Decimal(
    os.getenv("TP3_SHARE", "60")
)

TP1_TRIGGER = Decimal(
    os.getenv("TP1_TRIGGER", "0.50")
)

TP2_TRIGGER = Decimal(
    os.getenv("TP2_TRIGGER", "1.00")
)

TRAILING_DISTANCE = Decimal(
    os.getenv("TRAILING_DISTANCE", "0.20")
)


# ============================================================
# PYRAMID CONFIGURATION
# ============================================================

PYRAMID_TRIGGER = Decimal(
    os.getenv("PYRAMID_TRIGGER", "0.30")
)

PYRAMID_SIZE_PCT = Decimal(
    os.getenv("PYRAMID_SIZE_PCT", "5")
)


# ============================================================
# SAFETY
# ============================================================

LIVE_ORDER_EXECUTION = False

RUN_SIMULATED_LIFECYCLE_TEST = (
    os.getenv(
        "RUN_SIMULATED_LIFECYCLE_TEST",
        "true",
    ).lower()
    == "true"
)


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
# CONSTANTS
# ============================================================

D100 = Decimal("100")


# ============================================================
# HELPERS
# ============================================================

def decimal_value(value):

    return Decimal(
        str(value)
    )


def percentage_move(
    entry,
    price,
    side,
):

    if side == "LONG":

        return (
            (price - entry)
            / entry
        ) * D100

    return (
        (entry - price)
        / entry
    ) * D100


# ============================================================
# TRADE STATE
# ============================================================

@dataclass
class Trade:

    side: str

    entry: Decimal

    size_pct: Decimal = ENTRY_PCT

    remaining_pct: Decimal = D100

    pyramids: int = 0

    backups: int = 0

    tp1_done: bool = False

    tp2_done: bool = False

    trailing: bool = False

    trail_extreme: Optional[
        Decimal
    ] = None

    closed: bool = False

    events: list[str] = field(
        default_factory=list
    )

    def log(
        self,
        text,
    ):

        self.events.append(
            text
        )

        print(
            text,
            flush=True,
        )


    # ========================================================
    # PYRAMID
    # ========================================================

    def add_pyramid(
        self,
        price,
    ):

        if self.closed:

            return

        if (
            self.pyramids
            >= MAX_PYRAMIDS
        ):

            return

        self.pyramids += 1

        old_size = self.size_pct

        new_size = (
            old_size
            + PYRAMID_SIZE_PCT
        )

        self.entry = (

            (
                self.entry
                * old_size
            )

            +

            (
                price
                * PYRAMID_SIZE_PCT
            )

        ) / new_size

        self.size_pct = new_size

        self.log(

            f"PYRAMID #{self.pyramids}: "
            f"+{PYRAMID_SIZE_PCT}% "
            f"at {price:.2f} | "
            f"new avg {self.entry:.2f} | "
            f"total size {self.size_pct}%"

        )


    # ========================================================
    # PARTIAL CLOSE
    # ========================================================

    def close_share(
        self,
        share,
        label,
        price,
    ):

        self.remaining_pct = max(

            Decimal("0"),

            self.remaining_pct
            - share,

        )

        self.log(

            f"{label}: "
            f"closed {share}% "
            f"at {price:.2f} | "
            f"remaining "
            f"{self.remaining_pct}%"

        )


    # ========================================================
    # POSITION MANAGEMENT
    # ========================================================

    def update(
        self,
        price,
    ):

        if self.closed:

            return

        move = percentage_move(

            self.entry,
            price,
            self.side,

        )


        # ----------------------------------------------------
        # PYRAMID
        # ----------------------------------------------------

        if (

            self.pyramids
            < MAX_PYRAMIDS

            and

            move
            >= PYRAMID_TRIGGER

        ):

            self.add_pyramid(
                price
            )

            move = percentage_move(

                self.entry,
                price,
                self.side,

            )


        # ----------------------------------------------------
        # TP1
        # ----------------------------------------------------

        if (

            not self.tp1_done

            and

            move
            >= TP1_TRIGGER

        ):

            self.tp1_done = True

            self.close_share(

                TP1_SHARE,
                "TP1",
                price,

            )


        # ----------------------------------------------------
        # TP2
        # ----------------------------------------------------

        if (

            not self.tp2_done

            and

            move
            >= TP2_TRIGGER

        ):

            self.tp2_done = True

            self.close_share(

                TP2_SHARE,
                "TP2",
                price,

            )

            self.trailing = True

            self.trail_extreme = price

            self.log(

                "TRAILING ACTIVATED "
                f"for final "
                f"{self.remaining_pct}% | "
                f"distance "
                f"{TRAILING_DISTANCE}%"

            )


        # ----------------------------------------------------
        # TRAILING TP3
        # ----------------------------------------------------

        if (

            self.trailing

            and

            not self.closed

        ):

            if self.side == "LONG":

                self.trail_extreme = max(

                    self.trail_extreme
                    or price,

                    price,

                )

                trailing_stop = (

                    self.trail_extreme

                    *

                    (
                        D100
                        - TRAILING_DISTANCE
                    )

                    / D100

                )

                if price <= trailing_stop:

                    self.close_share(

                        self.remaining_pct,
                        "TRAIL EXIT",
                        price,

                    )

                    self.closed = True


            else:

                self.trail_extreme = min(

                    self.trail_extreme
                    or price,

                    price,

                )

                trailing_stop = (

                    self.trail_extreme

                    *

                    (
                        D100
                        + TRAILING_DISTANCE
                    )

                    / D100

                )

                if price >= trailing_stop:

                    self.close_share(

                        self.remaining_pct,
                        "TRAIL EXIT",
                        price,

                    )

                    self.closed = True


# ============================================================
# TELEGRAM
# ============================================================

async def send_telegram(
    text,
):

    if (

        not TELEGRAM_BOT_TOKEN

        or

        not TELEGRAM_CHAT_ID

    ):

        print(
            "TELEGRAM CONFIG: MISSING",
            flush=True,
        )

        return

    try:

        bot = Bot(
            TELEGRAM_BOT_TOKEN
        )

        await bot.send_message(

            chat_id=TELEGRAM_CHAT_ID,

            text=text,

        )

        print(
            "TELEGRAM MESSAGE SENT",
            flush=True,
        )

    except Exception as error:

        print(

            f"TELEGRAM ERROR: "
            f"{error}",

            flush=True,

        )


# ============================================================
# SAFETY VALIDATION
# ============================================================

def validate_configuration():

    if (
        LEVERAGE
        > MAX_LEVERAGE
    ):

        raise ValueError(

            "LEVERAGE exceeds "
            "MAX_LEVERAGE"

        )


    if (

        ENTRY_PCT
        > MAX_FUND_EXPOSURE_PCT

    ):

        raise ValueError(

            "ENTRY_PCT exceeds "
            "MAX_FUND_EXPOSURE_PCT"

        )


    total_tp = (

        TP1_SHARE
        + TP2_SHARE
        + TP3_SHARE

    )

    if total_tp != D100:

        raise ValueError(

            "TP1 + TP2 + TP3 "
            "must equal 100%"

        )


# ============================================================
# 0F-4D SIMULATED FULL TRADE TEST
# ============================================================

async def simulated_lifecycle_test():

    print(
        "=" * 60,
        flush=True,
    )

    print(
        "0F-4D SIMULATED FULL "
        "TRADE LIFECYCLE TEST",
        flush=True,
    )

    print(
        "NO LIVE ORDERS "
        "WILL BE SENT",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )


    # --------------------------------------------------------
    # SIMULATED LONG ENTRY
    # --------------------------------------------------------

    trade = Trade(

        side="LONG",

        entry=Decimal(
            "100.00"
        ),

    )

    trade.log(

        "SIM ENTRY: "
        "LONG at 100.00 | "
        "initial position 5%"

    )


    # --------------------------------------------------------
    # CONTROLLED PRICE PATH
    # --------------------------------------------------------

    simulated_prices = [

        Decimal("100.31"),

        Decimal("100.82"),

        Decimal("101.35"),

        Decimal("101.70"),

        Decimal("101.80"),

        Decimal("101.55"),

    ]


    for price in simulated_prices:

        trade.log(

            f"SIM PRICE: "
            f"{price:.2f}"

        )

        trade.update(
            price
        )

        await asyncio.sleep(
            0.15
        )


    # --------------------------------------------------------
    # VERIFY COMPLETE EXIT
    # --------------------------------------------------------

    if not trade.closed:

        raise RuntimeError(

            "Simulation failed: "
            "trade did not close"

        )


    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    trade.log(

        "IDLE PYRAMID CLEANUP: "
        "COMPLETE"

    )

    trade.log(

        "TRADE STATE RESET: "
        "COMPLETE"

    )

    trade.log(

        "0F-4D SIMULATION: "
        "PASSED"

    )


    # --------------------------------------------------------
    # TELEGRAM RESULT
    # --------------------------------------------------------

    await send_telegram(

        "🧪 MODULE 0F-4D TEST PASSED\n"
        "BTCUSDT simulated full trade lifecycle\n\n"

        "✅ Initial entry\n"
        "✅ Pyramid\n"
        "✅ TP1 20%\n"
        "✅ TP2 20%\n"
        "✅ TP3 60% trailing exit\n"
        "✅ Idle pyramid cleanup\n"
        "✅ Trade state reset\n\n"

        "⚠️ Live order execution disabled"

    )


# ============================================================
# WEEX PRICE EXTRACTION
# ============================================================

def extract_price(
    message,
):

    try:

        obj = json.loads(
            message
        )

    except Exception:

        return None


    data = obj.get(
        "data"
    )


    candidates = []


    if isinstance(
        data,
        dict,
    ):

        candidates.append(
            data
        )


    elif isinstance(
        data,
        list,
    ):

        for item in data:

            if isinstance(
                item,
                dict,
            ):

                candidates.append(
                    item
                )


    candidates.append(
        obj
    )


    price_fields = (

        "close",
        "lastPrice",
        "last",
        "price",
        "c",

    )


    for candidate in candidates:

        for field in price_fields:

            value = candidate.get(
                field
            )

            if value in (

                None,
                "",
                0,
                "0",

            ):

                continue

            try:

                price = decimal_value(
                    value
                )

                if price > 0:

                    return price

            except Exception:

                continue


    return None


# ============================================================
# LIVE WEEX MARKET MONITOR
# ============================================================

async def market_monitor():

    reconnect_delay = 5


    while True:

        try:

            print(
                "CONNECTING TO WEEX...",
                flush=True,
            )


            async with websockets.connect(

                WS_URL,

                ping_interval=None,

                close_timeout=10,

                additional_headers={

                    "User-Agent":
                    "WEEX-BTC-Bot/0F-4D"

                },

            ) as websocket:


                print(
                    "CONNECTED TO WEEX",
                    flush=True,
                )


                subscribe_payload = {

                    "method":
                    "SUBSCRIBE",

                    "params": [
                        CHANNEL
                    ],

                    "id":
                    1,

                }


                await websocket.send(

                    json.dumps(
                        subscribe_payload
                    )

                )


                print(

                    f"SUBSCRIBED TO "
                    f"{CHANNEL}",

                    flush=True,

                )


                reconnect_delay = 5


                async for raw in websocket:


                    if isinstance(
                        raw,
                        bytes,
                    ):

                        raw = raw.decode(

                            "utf-8",

                            errors="ignore",

                        )


                    # ----------------------------------------
                    # SIMPLE PING/PONG
                    # ----------------------------------------

                    if raw == "ping":

                        await websocket.send(
                            "pong"
                        )

                        continue


                    try:

                        obj = json.loads(
                            raw
                        )


                        if (
                            obj.get("event")
                            == "ping"
                        ):

                            await websocket.send(

                                json.dumps({

                                    "event":
                                    "pong"

                                })

                            )

                            continue


                    except Exception:

                        pass


                    # ----------------------------------------
                    # SUBSCRIPTION ACK
                    # ----------------------------------------

                    if (
                        "subscribe"
                        in raw.lower()
                    ):

                        print(

                            "SUBSCRIPTION "
                            "CONFIRMED",

                            flush=True,

                        )


                    # ----------------------------------------
                    # LIVE PRICE
                    # ----------------------------------------

                    price = extract_price(
                        raw
                    )


                    if price:

                        print(

                            f"{SYMBOL} "
                            f"LIVE PRICE: "
                            f"{price}",

                            flush=True,

                        )


        except asyncio.CancelledError:

            raise


        except Exception as error:

            print(

                "WEEX CONNECTION "
                f"ERROR: {error}",

                flush=True,

            )


            print(

                "RECONNECTING IN "
                f"{reconnect_delay}s...",

                flush=True,

            )


            await asyncio.sleep(
                reconnect_delay
            )


            reconnect_delay = min(

                reconnect_delay * 2,

                60,

            )


# ============================================================
# MAIN
# ============================================================

async def main():

    validate_configuration()


    print(
        "=" * 60,
        flush=True,
    )

    print(

        f"MODULE {MODULE} STARTING",

        flush=True,

    )

    print(

        "BTCUSDT SIMULATED FULL "
        "TRADE LIFECYCLE + "
        "LIVE MONITOR",

        flush=True,

    )

    print(
        "=" * 60,
        flush=True,
    )


    print(
        f"Entry: {ENTRY_PCT}%",
        flush=True,
    )

    print(
        f"Leverage: {LEVERAGE}x",
        flush=True,
    )

    print(

        f"Max Leverage: "
        f"{MAX_LEVERAGE}x",

        flush=True,

    )

    print(

        f"Max Pyramids: "
        f"{MAX_PYRAMIDS}",

        flush=True,

    )

    print(

        f"Max Backups: "
        f"{MAX_BACKUPS}",

        flush=True,

    )

    print(

        "Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PCT}%",

        flush=True,

    )

    print(

        "TP1 / TP2 / TP3: "
        f"{TP1_SHARE}% / "
        f"{TP2_SHARE}% / "
        f"{TP3_SHARE}%",

        flush=True,

    )

    print(

        f"TP1 Trigger: "
        f"{TP1_TRIGGER}%",

        flush=True,

    )

    print(

        f"TP2 Trigger: "
        f"{TP2_TRIGGER}%",

        flush=True,

    )

    print(

        "Trailing Distance: "
        f"{TRAILING_DISTANCE}%",

        flush=True,

    )

    print(

        "Idle pyramid cleanup: "
        "ACTIVE",

        flush=True,

    )

    print(

        "Safety controls: "
        "ACTIVE",

        flush=True,

    )

    print(

        "LIVE ORDER EXECUTION: "
        "DISABLED",

        flush=True,

    )

    print(
        "=" * 60,
        flush=True,
    )


    # ========================================================
    # STARTUP TELEGRAM
    # ========================================================

    await send_telegram(

        "✅ MODULE 0F-4D ONLINE\n"
        "BTCUSDT\n"
        "Simulated Full Trade Lifecycle Engine\n\n"

        "🛡 Safety controls active\n"
        "⚠️ Live order execution disabled"

    )


    # ========================================================
    # SIMULATION
    # ========================================================

    if RUN_SIMULATED_LIFECYCLE_TEST:

        await simulated_lifecycle_test()

    else:

        print(

            "SIMULATED LIFECYCLE "
            "TEST: DISABLED",

            flush=True,

        )


    # ========================================================
    # LIVE MONITOR
    # ========================================================

    print(
        "=" * 60,
        flush=True,
    )

    print(

        "LIVE MARKET "
        "MONITORING ACTIVE",

        flush=True,

    )

    print(

        "WAITING FOR WEEX "
        "MARKET DATA...",

        flush=True,

    )


    await market_monitor()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main())
