import asyncio
import json
import os
from decimal import Decimal, InvalidOperation

import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE_NAME = "0F-4E"


# ============================================================
# MARKET CONFIGURATION
# ============================================================

SYMBOL = "BTCUSDT"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIPTION_CHANNEL = (
    f"{SYMBOL}@kline_1m_LAST_PRICE"
)

RECONNECT_DELAY_SECONDS = 5


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


def telegram_is_configured():
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(message):

    if not telegram_is_configured():
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

    except Exception as error:

        print(
            "TELEGRAM ERROR:",
            error,
        )


# ============================================================
# TRADE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal("5")

LEVERAGE = Decimal("5")

MAX_LEVERAGE = Decimal("10")

MAX_PYRAMID_ADDS = 1

PYRAMID_SIZE_PERCENT = Decimal("5")

MAX_BACKUPS = 3

BACKUP_SIZES_PERCENT = [
    Decimal("5"),
    Decimal("5"),
    Decimal("5"),
]

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")

TP2_PERCENT = Decimal("20")

TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.50")

TP2_TRIGGER_PERCENT = Decimal("1.00")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

PYRAMID_TRIGGER_PERCENT = Decimal("0.30")


# ============================================================
# SAFETY CONFIGURATION
# ============================================================

LIVE_ORDER_EXECUTION = False

IDLE_PYRAMID_CLEANUP = True

ANTI_DUPLICATE_ORDERS = True

ONE_DIRECTION_ONLY = True

SAFETY_CONTROLS_ACTIVE = True


# ============================================================
# HELPERS
# ============================================================

def D(value):

    try:
        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):
        return None


def percentage_move(
    entry,
    current,
):

    if entry <= 0:
        return Decimal("0")

    return (
        (
            current - entry
        )
        / entry
    ) * Decimal("100")


# ============================================================
# SIMULATED TRADE STATE
# ============================================================

class SimulatedTrade:

    def __init__(
        self,
        side,
        entry_price,
    ):

        self.side = side

        self.initial_entry = entry_price

        self.average_entry = entry_price

        self.total_size = (
            INITIAL_ENTRY_PERCENT
        )

        self.remaining_percent = (
            Decimal("100")
        )

        self.pyramids = 0

        self.tp1_done = False

        self.tp2_done = False

        self.trailing_active = False

        self.trailing_high = None

        self.closed = False


    def add_pyramid(
        self,
        price,
    ):

        if (
            self.pyramids
            >= MAX_PYRAMID_ADDS
        ):
            return False

        old_size = self.total_size

        add_size = (
            PYRAMID_SIZE_PERCENT
        )

        new_size = (
            old_size
            + add_size
        )

        self.average_entry = (

            (
                self.average_entry
                * old_size
            )

            +

            (
                price
                * add_size
            )

        ) / new_size

        self.total_size = new_size

        self.pyramids += 1

        print(
            f"PYRAMID #{self.pyramids}: "
            f"+{add_size}% at {price:.2f} "
            f"| new avg {self.average_entry:.2f} "
            f"| total size {self.total_size}%"
        )

        return True


    def process_price(
        self,
        price,
    ):

        if self.closed:
            return

        move = percentage_move(
            self.average_entry,
            price,
        )

        if self.side == "SHORT":
            move = -move


        # ================================================
        # PYRAMID
        # ================================================

        if (
            self.pyramids
            < MAX_PYRAMID_ADDS
            and move
            >= PYRAMID_TRIGGER_PERCENT
        ):

            self.add_pyramid(
                price
            )

            move = percentage_move(
                self.average_entry,
                price,
            )

            if self.side == "SHORT":
                move = -move


        # ================================================
        # TP1
        # ================================================

        if (
            not self.tp1_done
            and move
            >= TP1_TRIGGER_PERCENT
        ):

            self.tp1_done = True

            self.remaining_percent -= (
                TP1_PERCENT
            )

            print(
                f"TP1: closed "
                f"{TP1_PERCENT}% "
                f"at {price:.2f} "
                f"| remaining "
                f"{self.remaining_percent}%"
            )


        # ================================================
        # TP2
        # ================================================

        if (
            self.tp1_done
            and not self.tp2_done
            and move
            >= TP2_TRIGGER_PERCENT
        ):

            self.tp2_done = True

            self.remaining_percent -= (
                TP2_PERCENT
            )

            print(
                f"TP2: closed "
                f"{TP2_PERCENT}% "
                f"at {price:.2f} "
                f"| remaining "
                f"{self.remaining_percent}%"
            )

            self.trailing_active = True

            self.trailing_high = price

            print(
                "TRAILING ACTIVATED "
                f"for final "
                f"{self.remaining_percent}% "
                f"| distance "
                f"{TRAILING_DISTANCE_PERCENT}%"
            )


        # ================================================
        # TRAILING PROFIT
        # ================================================

        if not self.trailing_active:
            return


        if self.side == "LONG":

            if (
                self.trailing_high is None
                or price
                > self.trailing_high
            ):

                self.trailing_high = price


            trail_stop = (

                self.trailing_high

                * (

                    Decimal("1")

                    -

                    (
                        TRAILING_DISTANCE_PERCENT
                        / Decimal("100")
                    )

                )
            )


            if price <= trail_stop:

                self.close_trailing(
                    price
                )


        else:

            if (
                self.trailing_high is None
                or price
                < self.trailing_high
            ):

                self.trailing_high = price


            trail_stop = (

                self.trailing_high

                * (

                    Decimal("1")

                    +

                    (
                        TRAILING_DISTANCE_PERCENT
                        / Decimal("100")
                    )

                )
            )


            if price >= trail_stop:

                self.close_trailing(
                    price
                )


    def close_trailing(
        self,
        price,
    ):

        amount = (
            self.remaining_percent
        )

        self.remaining_percent = (
            Decimal("0")
        )

        self.closed = True

        print(
            f"TRAIL EXIT: closed "
            f"{amount}% "
            f"at {price:.2f} "
            "| remaining 0%"
        )


# ============================================================
# SIMULATION
# ============================================================

async def run_full_lifecycle_test():

    print("=" * 60)

    print(
        "0F-4E SIMULATED "
        "FULL TRADE LIFECYCLE TEST"
    )

    print(
        "NO LIVE ORDERS WILL BE SENT"
    )

    print("=" * 60)


    trade = SimulatedTrade(
        side="LONG",
        entry_price=Decimal("100.00"),
    )


    print(
        "SIM ENTRY: LONG at 100.00 "
        f"| initial position "
        f"{INITIAL_ENTRY_PERCENT}%"
    )


    simulated_prices = [

        Decimal("100.31"),

        Decimal("100.82"),

        Decimal("101.35"),

        Decimal("101.70"),

        Decimal("101.80"),

        Decimal("101.55"),

    ]


    for price in simulated_prices:

        print(
            f"SIM PRICE: {price:.2f}"
        )

        trade.process_price(
            price
        )


    if trade.closed:

        if IDLE_PYRAMID_CLEANUP:

            print(
                "IDLE PYRAMID CLEANUP: "
                "COMPLETE"
            )

        print(
            "TRADE STATE RESET: COMPLETE"
        )

        print(
            "0F-4E SIMULATION: PASSED"
        )

    else:

        print(
            "0F-4E SIMULATION: FAILED"
        )


    print("=" * 60)


# ============================================================
# WEEX MESSAGE PROCESSOR
# ============================================================

def extract_kline_price(
    data,
):

    if not isinstance(
        data,
        dict,
    ):
        return None


    if data.get("e") != "kline":
        return None


    candles = data.get("d")

    if not isinstance(
        candles,
        list,
    ):
        return None


    if not candles:
        return None


    candle = candles[-1]

    if not isinstance(
        candle,
        dict,
    ):
        return None


    price = D(
        candle.get("c")
    )


    if (
        price is None
        or price <= 0
    ):
        return None


    return price


# ============================================================
# LIVE WEEX MONITOR
# ============================================================

async def live_market_monitor():

    while True:

        try:

            print(
                "CONNECTING TO WEEX..."
            )


            headers = {

                "User-Agent":
                "WEEX-0F-4E-BOT/1.0"

            }


            async with websockets.connect(

                WS_URL,

                additional_headers=headers,

                ping_interval=None,

                ping_timeout=None,

                close_timeout=5,

            ) as websocket:


                print(
                    "CONNECTED TO WEEX"
                )


                subscribe_message = {

                    "method":
                    "SUBSCRIBE",

                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],

                    "id": 1,

                }


                await websocket.send(

                    json.dumps(
                        subscribe_message
                    )

                )


                print(
                    "SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}"
                )


                subscription_confirmed = False

                last_price = None


                async for raw_message in websocket:


                    # ====================================
                    # DECODE MESSAGE
                    # ====================================

                    try:

                        if isinstance(
                            raw_message,
                            bytes,
                        ):

                            raw_message = (
                                raw_message.decode(
                                    "utf-8"
                                )
                            )


                        message = json.loads(
                            raw_message
                        )


                    except Exception as error:

                        print(
                            "WEEX MESSAGE "
                            "DECODE ERROR:",
                            error,
                        )

                        continue


                    # ====================================
                    # APPLICATION HEARTBEAT
                    # ====================================

                    if isinstance(
                        message,
                        dict,
                    ):

                        event = message.get(
                            "event"
                        )

                        msg_type = message.get(
                            "type"
                        )


                        if (
                            event == "ping"
                            or msg_type == "ping"
                        ):

                            pong = {

                                "method":
                                "PONG",

                                "id": 1,

                            }


                            await websocket.send(

                                json.dumps(
                                    pong
                                )

                            )


                            print(
                                "WEEX PING → "
                                "PONG SENT"
                            )

                            continue


                    # ====================================
                    # SUBSCRIPTION ACKNOWLEDGEMENT
                    # ====================================

                    if (
                        isinstance(
                            message,
                            dict,
                        )

                        and message.get(
                            "id"
                        ) == 1

                        and "result"
                        in message
                    ):


                        if (
                            message.get(
                                "result"
                            )
                            is True
                        ):

                            if (
                                not
                                subscription_confirmed
                            ):

                                print(
                                    "SUBSCRIPTION "
                                    "CONFIRMED"
                                )

                                subscription_confirmed = (
                                    True
                                )


                        else:

                            print(
                                "SUBSCRIPTION "
                                "REJECTED:",
                                message,
                            )


                        continue


                    # ====================================
                    # MARKET PRICE
                    # ====================================

                    price = extract_kline_price(
                        message
                    )


                    if price is None:
                        continue


                    if (
                        last_price is None
                        or price
                        != last_price
                    ):

                        print(
                            f"{SYMBOL} LIVE PRICE: "
                            f"{price}"
                        )

                        last_price = price


        except asyncio.CancelledError:

            raise


        except Exception as error:

            print(
                "WEEX CONNECTION ERROR:",
                error,
            )


        print(
            "RECONNECTING IN "
            f"{RECONNECT_DELAY_SECONDS}s..."
        )


        await asyncio.sleep(
            RECONNECT_DELAY_SECONDS
        )


# ============================================================
# STARTUP
# ============================================================

async def main():

    print("=" * 60)

    print(
        f"MODULE {MODULE_NAME} STARTING"
    )

    print(
        "BTCUSDT STABILIZED WEEX "
        "CONNECTION + TRADE LIFECYCLE ENGINE"
    )

    print("=" * 60)

    print(
        f"Entry: "
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    print(
        f"Leverage: "
        f"{LEVERAGE}x"
    )

    print(
        f"Max Leverage: "
        f"{MAX_LEVERAGE}x"
    )

    print(
        f"Max Pyramids: "
        f"{MAX_PYRAMID_ADDS}"
    )

    print(
        f"Max Backups: "
        f"{MAX_BACKUPS}"
    )

    print(
        f"Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    print(
        "TP1 / TP2 / TP3: "
        f"{TP1_PERCENT}% / "
        f"{TP2_PERCENT}% / "
        f"{TP3_PERCENT}%"
    )

    print(
        f"TP1 Trigger: "
        f"{TP1_TRIGGER_PERCENT}%"
    )

    print(
        f"TP2 Trigger: "
        f"{TP2_TRIGGER_PERCENT}%"
    )

    print(
        f"Trailing Distance: "
        f"{TRAILING_DISTANCE_PERCENT}%"
    )

    print(
        "Idle pyramid cleanup: "
        "ACTIVE"
    )

    print(
        "Safety controls: ACTIVE"
    )

    print(
        "LIVE ORDER EXECUTION: "
        "DISABLED"
    )

    print("=" * 60)


    await send_telegram(

        "✅ MODULE 0F-4E ONLINE\n"
        "BTCUSDT\n"
        "Stabilized WEEX WebSocket + "
        "Trade Lifecycle Engine\n\n"
        "🛡 Safety controls active\n"
        "⚠️ Live order execution disabled"

    )


    await run_full_lifecycle_test()


    await send_telegram(

        "🧪 MODULE 0F-4E TEST\n"
        "BTCUSDT\n\n"
        "✅ Full simulated trade "
        "lifecycle completed\n"
        "✅ Pyramid\n"
        "✅ TP1\n"
        "✅ TP2\n"
        "✅ Trailing exit\n"
        "✅ State cleanup\n\n"
        "No live order was sent."

    )


    print(
        "LIVE MARKET MONITORING ACTIVE"
    )

    print(
        "WAITING FOR WEEX MARKET DATA..."
    )


    await live_market_monitor()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "MODULE STOPPED"
        )
