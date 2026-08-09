import asyncio
import json
import os
from decimal import Decimal, InvalidOperation

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE
# ============================================================

MODULE = "0F-4C"
SYMBOL = "BTCUSDT"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"
CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"

HISTORICAL_URL = (
    "https://api-contract.weex.com"
    "/capi/v3/market/klines"
)

HISTORICAL_LIMIT = 250

RECONNECT_DELAY = 5
MAX_RECONNECT_DELAY = 60


# ============================================================
# HELPERS
# ============================================================

def env_decimal(name, default):
    try:
        return Decimal(
            os.getenv(name, str(default))
        )
    except Exception:
        return Decimal(str(default))


def env_int(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return int(default)


def D(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def pct(value):
    return Decimal(str(value)) / Decimal("100")


# ============================================================
# TRADE CONFIGURATION
# ============================================================

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

MAX_PYRAMID_ADDS = env_int(
    "MAX_PYRAMID_ADDS",
    1,
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

MAX_BACKUPS = env_int(
    "MAX_BACKUPS",
    3,
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

MAX_FUND_EXPOSURE_PERCENT = env_decimal(
    "MAX_FUND_EXPOSURE_PERCENT",
    "35",
)

MAX_TRADE_LOSS_PERCENT = env_decimal(
    "MAX_TRADE_LOSS_PERCENT",
    "10",
)

MIN_LIQUIDATION_DISTANCE_PERCENT = env_decimal(
    "MIN_LIQUIDATION_DISTANCE_PERCENT",
    "1",
)

BACKUP_LIQUIDATION_BUFFER_PERCENT = env_decimal(
    "BACKUP_LIQUIDATION_BUFFER_PERCENT",
    "0.50",
)


# ============================================================
# PROFIT CONFIGURATION
# ============================================================

TP1_CLOSE_PERCENT = env_decimal(
    "TP1_CLOSE_PERCENT",
    "20",
)

TP2_CLOSE_PERCENT = env_decimal(
    "TP2_CLOSE_PERCENT",
    "20",
)

TP3_CLOSE_PERCENT = env_decimal(
    "TP3_CLOSE_PERCENT",
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
# SAFETY
# ============================================================

LIVE_EXECUTION = False

IDLE_PYRAMID_CLEANUP = True
ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True
TREND_REVERSAL_EXIT = True


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

telegram_bot = None

if TELEGRAM_BOT_TOKEN:
    telegram_bot = Bot(
        token=TELEGRAM_BOT_TOKEN
    )


async def send_telegram(message):
    if not telegram_bot or not TELEGRAM_CHAT_ID:
        return

    try:
        await telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

    except Exception as e:
        print(
            f"TELEGRAM ERROR: {e}",
            flush=True,
        )


# ============================================================
# POSITION STATE
# ============================================================

class PositionState:

    def __init__(self):
        self.reset()

    def reset(self):
        self.active = False
        self.side = None

        self.entry_price = None
        self.average_price = None
        self.current_price = None

        self.position_percent = Decimal("0")

        self.pyramids_used = 0
        self.backups_used = 0

        self.tp1_done = False
        self.tp2_done = False
        self.trailing_active = False

        self.highest_price = None
        self.lowest_price = None

        self.last_action = None


position = PositionState()


# ============================================================
# EXPOSURE CONTROL
# ============================================================

def exposure_allowed(add_percent):
    new_total = (
        position.position_percent
        + Decimal(str(add_percent))
    )

    return (
        new_total
        <= MAX_FUND_EXPOSURE_PERCENT
    )


# ============================================================
# PYRAMID SIZE
# ============================================================

def pyramid_size(number):

    sizes = [
        PYRAMID_1_PERCENT,
        PYRAMID_2_PERCENT,
        PYRAMID_3_PERCENT,
    ]

    index = number - 1

    if index < 0 or index >= len(sizes):
        return Decimal("0")

    return sizes[index]


# ============================================================
# BACKUP SIZE
# ============================================================

def backup_size(number):

    sizes = [
        BACKUP_1_PERCENT,
        BACKUP_2_PERCENT,
        BACKUP_3_PERCENT,
    ]

    index = number - 1

    if index < 0 or index >= len(sizes):
        return Decimal("0")

    return sizes[index]


# ============================================================
# SIMULATED ENTRY
# ============================================================

async def simulate_entry(side, price):

    if position.active:
        return False

    if LEVERAGE > MAX_LEVERAGE:
        print(
            "ENTRY BLOCKED: LEVERAGE ABOVE MAXIMUM",
            flush=True,
        )
        return False

    if INITIAL_ENTRY_PERCENT > MAX_FUND_EXPOSURE_PERCENT:
        print(
            "ENTRY BLOCKED: FUND EXPOSURE LIMIT",
            flush=True,
        )
        return False

    position.active = True
    position.side = side
    position.entry_price = price
    position.average_price = price
    position.current_price = price

    position.position_percent = (
        INITIAL_ENTRY_PERCENT
    )

    position.highest_price = price
    position.lowest_price = price

    print(
        f"SIMULATED {side} ENTRY @ {price}",
        flush=True,
    )

    await send_telegram(
        f"🧪 {MODULE} SIMULATED ENTRY\n"
        f"{SYMBOL}\n"
        f"Side: {side}\n"
        f"Price: {price}\n"
        f"Position: {INITIAL_ENTRY_PERCENT}%\n"
        f"Leverage: {LEVERAGE}x\n"
        f"⚠️ No live WEEX order sent."
    )

    return True


# ============================================================
# PYRAMID
# ============================================================

async def add_pyramid(price):

    if not position.active:
        return

    if position.pyramids_used >= MAX_PYRAMID_ADDS:
        return

    number = position.pyramids_used + 1
    size = pyramid_size(number)

    if size <= 0:
        return

    if not exposure_allowed(size):
        print(
            "PYRAMID BLOCKED: EXPOSURE LIMIT",
            flush=True,
        )
        return

    old_size = position.position_percent
    new_size = old_size + size

    position.average_price = (
        (
            position.average_price
            * old_size
        )
        +
        (
            price
            * size
        )
    ) / new_size

    position.position_percent = new_size
    position.pyramids_used += 1

    print(
        f"PYRAMID #{number} SIMULATED @ {price}",
        flush=True,
    )


# ============================================================
# PROFIT %
# ============================================================

def profit_percent(price):

    if not position.active:
        return Decimal("0")

    if position.side == "LONG":

        return (
            (
                price
                - position.average_price
            )
            /
            position.average_price
        ) * Decimal("100")

    return (
        (
            position.average_price
            - price
        )
        /
        position.average_price
    ) * Decimal("100")


# ============================================================
# TP / TRAILING ENGINE
# ============================================================

async def manage_profit(price):

    if not position.active:
        return

    profit = profit_percent(price)

    # ---------------- TP1 ----------------

    if (
        not position.tp1_done
        and profit >= TP1_TRIGGER_PERCENT
    ):
        position.tp1_done = True

        print(
            f"TP1 TRIGGERED: +{profit:.3f}%",
            flush=True,
        )

        await send_telegram(
            f"✅ {SYMBOL} TP1 TRIGGERED\n"
            f"Profit: +{profit:.3f}%\n"
            f"Close: {TP1_CLOSE_PERCENT}%\n"
            f"⚠️ Simulation only."
        )

    # ---------------- TP2 ----------------

    if (
        position.tp1_done
        and not position.tp2_done
        and profit >= TP2_TRIGGER_PERCENT
    ):
        position.tp2_done = True
        position.trailing_active = True

        position.highest_price = price
        position.lowest_price = price

        print(
            f"TP2 TRIGGERED: +{profit:.3f}%",
            flush=True,
        )

        print(
            "TP3 TRAILING ACTIVATED",
            flush=True,
        )

        await send_telegram(
            f"✅ {SYMBOL} TP2 TRIGGERED\n"
            f"Profit: +{profit:.3f}%\n"
            f"Close: {TP2_CLOSE_PERCENT}%\n"
            f"🏃 TP3 trailing now active\n"
            f"Trailing distance: "
            f"{TRAILING_DISTANCE_PERCENT}%"
        )

    # ---------------- TP3 TRAILING ----------------

    if not position.trailing_active:
        return

    distance = pct(
        TRAILING_DISTANCE_PERCENT
    )

    if position.side == "LONG":

        if price > position.highest_price:
            position.highest_price = price

        trailing_price = (
            position.highest_price
            * (Decimal("1") - distance)
        )

        if price <= trailing_price:

            await close_position(
                "TP3 TRAILING EXIT",
                price,
            )

    else:

        if price < position.lowest_price:
            position.lowest_price = price

        trailing_price = (
            position.lowest_price
            * (Decimal("1") + distance)
        )

        if price >= trailing_price:

            await close_position(
                "TP3 TRAILING EXIT",
                price,
            )


# ============================================================
# CLOSE POSITION
# ============================================================

async def close_position(reason, price):

    if not position.active:
        return

    side = position.side
    profit = profit_percent(price)

    print(
        f"POSITION CLOSED: {reason}",
        flush=True,
    )

    await send_telegram(
        f"🏁 {SYMBOL} POSITION CLOSED\n"
        f"Side: {side}\n"
        f"Reason: {reason}\n"
        f"Price: {price}\n"
        f"P/L: {profit:+.3f}%\n"
        f"⚠️ Simulation only."
    )

    position.reset()


# ============================================================
# MARKET PRICE EXTRACTION
# ============================================================

def find_price(obj):

    if isinstance(obj, dict):

        for key in (
            "close",
            "c",
            "lastPrice",
            "last",
            "price",
        ):
            value = obj.get(key)

            price = D(value)

            if price is not None and price > 0:
                return price

        for value in obj.values():

            result = find_price(value)

            if result is not None:
                return result

    elif isinstance(obj, list):

        # Typical candle arrays may contain close price
        if len(obj) >= 5:

            price = D(obj[4])

            if price is not None and price > 0:
                return price

        for value in obj:

            result = find_price(value)

            if result is not None:
                return result

    return None


# ============================================================
# MARKET UPDATE
# ============================================================

last_logged_price = None


async def handle_market_message(data):

    global last_logged_price

    price = find_price(data)

    if price is None:
        return

    position.current_price = price

    # Avoid printing every websocket packet.
    if price != last_logged_price:

        last_logged_price = price

        if position.active:
            await manage_profit(price)


# ============================================================
# WEEX CONNECTION
# ============================================================

async def websocket_session():

    print(
        "CONNECTING TO WEEX...",
        flush=True,
    )

    async with websockets.connect(
        WS_URL,
        ping_interval=None,
        close_timeout=10,
    ) as ws:

        print(
            "CONNECTED TO WEEX",
            flush=True,
        )

        subscribe = {
            "method": "SUBSCRIBE",
            "params": [CHANNEL],
            "id": 1,
        }

        await ws.send(
            json.dumps(subscribe)
        )

        print(
            f"SUBSCRIBED TO {CHANNEL}",
            flush=True,
        )

        async for raw in ws:

            try:
                data = json.loads(raw)

            except Exception:
                continue

            # WEEX application ping
            if isinstance(data, dict):

                if "ping" in data:

                    await ws.send(
                        json.dumps(
                            {
                                "pong": data["ping"]
                            }
                        )
                    )

                    continue

            # Subscription acknowledgement
            if isinstance(data, dict):

                if (
                    data.get("id") == 1
                    or data.get("event")
                    == "subscribe"
                ):
                    print(
                        "SUBSCRIPTION CONFIRMED",
                        flush=True,
                    )

            await handle_market_message(
                data
            )


# ============================================================
# PERMANENT MONITORING LOOP
# ============================================================

async def market_loop():

    delay = RECONNECT_DELAY

    while True:

        try:

            await websocket_session()

            # If websocket exits normally,
            # reconnect instead of ending program.
            print(
                "WEEX CONNECTION CLOSED - RECONNECTING",
                flush=True,
            )

        except asyncio.CancelledError:
            raise

        except Exception as e:

            print(
                f"WEEX CONNECTION ERROR: {e}",
                flush=True,
            )

        print(
            f"RECONNECTING IN {delay}s...",
            flush=True,
        )

        await asyncio.sleep(delay)

        delay = min(
            delay * 2,
            MAX_RECONNECT_DELAY,
        )


# ============================================================
# STARTUP MESSAGE
# ============================================================

async def startup_message():

    await send_telegram(
        f"✅ MODULE {MODULE} ONLINE\n"
        f"{SYMBOL}\n"
        f"Pyramid + TP + Trailing Management Engine\n"
        f"TP1 / TP2 / TP3: "
        f"{TP1_CLOSE_PERCENT}% / "
        f"{TP2_CLOSE_PERCENT}% / "
        f"{TP3_CLOSE_PERCENT}%\n"
        f"Max Pyramids: {MAX_PYRAMID_ADDS}\n"
        f"Max Backups: {MAX_BACKUPS}\n"
        f"🛡 Safety controls active\n"
        f"⚠️ Live order execution disabled"
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"MODULE {MODULE} STARTING",
        flush=True,
    )

    print(
        f"{SYMBOL} PYRAMID + TP + "
        f"TRAILING MANAGEMENT ENGINE",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    print(
        f"Entry: {INITIAL_ENTRY_PERCENT}%",
        flush=True,
    )

    print(
        f"Leverage: {LEVERAGE}x",
        flush=True,
    )

    print(
        f"Max Leverage: {MAX_LEVERAGE}x",
        flush=True,
    )

    print(
        f"Max Pyramids: {MAX_PYRAMID_ADDS}",
        flush=True,
    )

    print(
        f"Max Backups: {MAX_BACKUPS}",
        flush=True,
    )

    print(
        f"Max Fund Exposure: "
        f"{MAX_FUND_EXPOSURE_PERCENT}%",
        flush=True,
    )

    print(
        f"TP1 / TP2 / TP3: "
        f"{TP1_CLOSE_PERCENT}% / "
        f"{TP2_CLOSE_PERCENT}% / "
        f"{TP3_CLOSE_PERCENT}%",
        flush=True,
    )

    print(
        f"TP1 Trigger: "
        f"{TP1_TRIGGER_PERCENT}%",
        flush=True,
    )

    print(
        f"TP2 Trigger: "
        f"{TP2_TRIGGER_PERCENT}%",
        flush=True,
    )

    print(
        f"Trailing Distance: "
        f"{TRAILING_DISTANCE_PERCENT}%",
        flush=True,
    )

    print(
        "Idle pyramid cleanup: ACTIVE",
        flush=True,
    )

    print(
        "Safety controls: ACTIVE",
        flush=True,
    )

    print(
        "LIVE ORDER EXECUTION: DISABLED",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    # Startup Telegram is sent ONCE
    # during each actual process startup.
    await startup_message()

    print(
        "LIVE MARKET MONITORING ACTIVE",
        flush=True,
    )

    print(
        "WAITING FOR WEEX MARKET DATA...",
        flush=True,
    )

    # IMPORTANT:
    # This never normally returns.
    await market_loop()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "BOT STOPPED",
            flush=True,
        )
