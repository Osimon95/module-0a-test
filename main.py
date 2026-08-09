import asyncio
import json
import os
import time
import uuid
from decimal import Decimal, InvalidOperation

import aiohttp
import websockets
from telegram import Bot


# ============================================================
# MODULE 0F-4F
# SAFE AUTHENTICATED ORDER BRIDGE
# ============================================================

MODULE_NAME = "0F-4F"
SYMBOL = "BTCUSDT"

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"
SUBSCRIPTION_CHANNEL = f"{SYMBOL}@kline_1m_LAST_PRICE"

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# ============================================================
# MASTER SAFETY SWITCH
# ============================================================

# DO NOT CHANGE THIS YET.
LIVE_ORDER_EXECUTION = False


# ============================================================
# TRADE CONFIGURATION
# ============================================================

INITIAL_ENTRY_PERCENT = Decimal("5")
LEVERAGE = Decimal("5")
MAX_LEVERAGE = Decimal("10")

MAX_PYRAMID_ADDS = 1
PYRAMID_ADD_PERCENT = Decimal("5")

MAX_BACKUPS = 3

BACKUP_SIZES_PERCENT = [
    Decimal("5"),
    Decimal("7.5"),
    Decimal("10"),
]

MAX_FUND_EXPOSURE_PERCENT = Decimal("35")

TP1_PERCENT = Decimal("20")
TP2_PERCENT = Decimal("20")
TP3_PERCENT = Decimal("60")

TP1_TRIGGER_PERCENT = Decimal("0.50")
TP2_TRIGGER_PERCENT = Decimal("1.00")

TRAILING_DISTANCE_PERCENT = Decimal("0.20")

MIN_LIQUIDATION_DISTANCE_PERCENT = Decimal("1")
BACKUP_LIQUIDATION_BUFFER_PERCENT = Decimal("0.25")

MAX_TRADE_LOSS_PERCENT = Decimal("10")

SIGNAL_EXPIRY_SECONDS = 180

ONE_DIRECTION_ONLY = True
ANTI_DUPLICATE_ORDERS = True

IDLE_PYRAMID_CLEANUP = True


# ============================================================
# WEEX API CREDENTIALS
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


def weex_credentials_ready():
    return all(
        [
            WEEX_API_KEY,
            WEEX_API_SECRET,
            WEEX_API_PASSPHRASE,
        ]
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


def telegram_ready():
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


async def send_telegram(message):

    if not telegram_ready():
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

    except Exception as exc:

        print(
            "TELEGRAM ERROR:",
            exc,
        )


# ============================================================
# BASIC HELPERS
# ============================================================

def D(value):

    try:
        return Decimal(str(value))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return None


def percent_change(
    start,
    current,
):

    start = D(start)
    current = D(current)

    if (
        start is None
        or current is None
        or start == 0
    ):
        return Decimal("0")

    return (
        (current - start)
        / start
        * Decimal("100")
    )


# ============================================================
# TRADE STATE
# ============================================================

class TradeState:

    def __init__(self):

        self.reset()

    def reset(self):

        self.active = False

        self.direction = None

        self.entry_price = None
        self.average_price = None

        self.total_size_percent = Decimal("0")

        self.pyramids = 0
        self.backups = 0

        self.tp1_done = False
        self.tp2_done = False

        self.trailing_active = False
        self.trailing_peak = None

        self.remaining_percent = Decimal("100")

        self.signal_time = None

        self.last_client_order_id = None


trade = TradeState()


# ============================================================
# CLIENT ORDER ID
# ============================================================

used_client_order_ids = set()


def new_client_order_id(
    purpose="entry",
):

    short_uuid = (
        uuid.uuid4()
        .hex[:8]
    )

    timestamp = int(
        time.time()
    )

    client_id = (
        f"04f-{purpose}-"
        f"{timestamp}-{short_uuid}"
    )

    # WEEX limit is 36 characters.
    client_id = client_id[:36]

    return client_id


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_order(order):

    errors = []

    required = [
        "symbol",
        "side",
        "positionSide",
        "type",
        "quantity",
        "newClientOrderId",
    ]

    for field in required:

        if not order.get(field):

            errors.append(
                f"MISSING {field}"
            )

    if order.get("symbol") != SYMBOL:

        errors.append(
            "INVALID SYMBOL"
        )

    if order.get("side") not in (
        "BUY",
        "SELL",
    ):

        errors.append(
            "INVALID SIDE"
        )

    if order.get(
        "positionSide"
    ) not in (
        "LONG",
        "SHORT",
    ):

        errors.append(
            "INVALID POSITION SIDE"
        )

    if order.get("type") not in (
        "MARKET",
        "LIMIT",
    ):

        errors.append(
            "INVALID ORDER TYPE"
        )

    quantity = D(
        order.get("quantity")
    )

    if (
        quantity is None
        or quantity <= 0
    ):

        errors.append(
            "INVALID QUANTITY"
        )

    client_id = order.get(
        "newClientOrderId"
    )

    if client_id:

        if len(client_id) > 36:

            errors.append(
                "CLIENT ORDER ID TOO LONG"
            )

        if (
            ANTI_DUPLICATE_ORDERS
            and client_id
            in used_client_order_ids
        ):

            errors.append(
                "DUPLICATE CLIENT ORDER ID"
            )

    return errors


# ============================================================
# ORDER BUILDER
# ============================================================

def build_market_order(
    direction,
    quantity,
    purpose="entry",
):

    direction = (
        direction.upper()
    )

    if direction == "LONG":

        side = "BUY"
        position_side = "LONG"

    elif direction == "SHORT":

        side = "SELL"
        position_side = "SHORT"

    else:

        raise ValueError(
            "Direction must be LONG or SHORT"
        )

    client_id = (
        new_client_order_id(
            purpose
        )
    )

    return {
        "symbol": SYMBOL,
        "side": side,
        "positionSide": position_side,
        "type": "MARKET",
        "quantity": str(quantity),
        "newClientOrderId": client_id,
    }


# ============================================================
# SAFE ORDER BRIDGE
# ============================================================

async def order_bridge(
    direction,
    quantity,
    purpose="entry",
):

    order = build_market_order(
        direction,
        quantity,
        purpose,
    )

    print(
        "=" * 60
    )

    print(
        "0F-4F ORDER BRIDGE"
    )

    print(
        "PURPOSE:",
        purpose.upper(),
    )

    print(
        "DIRECTION:",
        direction,
    )

    print(
        "ORDER PAYLOAD:"
    )

    print(
        json.dumps(
            order,
            indent=2,
        )
    )

    errors = validate_order(
        order
    )

    if errors:

        print(
            "ORDER VALIDATION: FAILED"
        )

        for error in errors:

            print(
                " -",
                error,
            )

        print(
            "ORDER BLOCKED"
        )

        return False

    print(
        "ORDER VALIDATION: PASSED"
    )

    if (
        not weex_credentials_ready()
    ):

        print(
            "WEEX API CREDENTIALS: MISSING"
        )

        print(
            "ORDER TRANSMISSION: BLOCKED"
        )

        return False

    print(
        "WEEX API CREDENTIALS: READY"
    )

    if not LIVE_ORDER_EXECUTION:

        print(
            "LIVE ORDER EXECUTION: DISABLED"
        )

        print(
            "VALIDATION MODE ONLY"
        )

        print(
            "NO ORDER SENT TO WEEX"
        )

        used_client_order_ids.add(
            order[
                "newClientOrderId"
            ]
        )

        return True

    # ========================================================
    # DELIBERATE SAFETY LOCK
    # ========================================================
    #
    # Authentication and actual POST transmission
    # will be introduced in the next controlled module.
    #
    # Even if LIVE_ORDER_EXECUTION is accidentally changed
    # to True here, this module STILL refuses to trade.
    # ========================================================

    print(
        "HARD SAFETY LOCK ACTIVE"
    )

    print(
        "0F-4F DOES NOT TRANSMIT "
        "LIVE ORDERS"
    )

    return False


# ============================================================
# POSITION MANAGEMENT
# ============================================================

def start_simulated_trade(
    direction,
    price,
):

    trade.reset()

    trade.active = True
    trade.direction = direction

    trade.entry_price = D(
        price
    )

    trade.average_price = D(
        price
    )

    trade.total_size_percent = (
        INITIAL_ENTRY_PERCENT
    )

    trade.remaining_percent = (
        Decimal("100")
    )

    trade.signal_time = (
        time.time()
    )

    print(
        f"SIM ENTRY: {direction}"
        f" at {price}"
        f" | initial position "
        f"{INITIAL_ENTRY_PERCENT}%"
    )


def add_pyramid(
    price,
):

    if not trade.active:
        return False

    if (
        trade.pyramids
        >= MAX_PYRAMID_ADDS
    ):
        return False

    old_size = (
        trade.total_size_percent
    )

    add_size = (
        PYRAMID_ADD_PERCENT
    )

    new_size = (
        old_size
        + add_size
    )

    old_value = (
        trade.average_price
        * old_size
    )

    new_value = (
        D(price)
        * add_size
    )

    trade.average_price = (
        old_value
        + new_value
    ) / new_size

    trade.total_size_percent = (
        new_size
    )

    trade.pyramids += 1

    print(
        f"PYRAMID #{trade.pyramids}: "
        f"+{add_size}% at {price}"
        f" | new avg "
        f"{trade.average_price:.2f}"
        f" | total size "
        f"{new_size}%"
    )

    return True


def take_profit_1(
    price,
):

    if (
        not trade.active
        or trade.tp1_done
    ):
        return

    trade.tp1_done = True

    trade.remaining_percent -= (
        TP1_PERCENT
    )

    print(
        f"TP1: closed "
        f"{TP1_PERCENT}% "
        f"at {price}"
        f" | remaining "
        f"{trade.remaining_percent}%"
    )


def take_profit_2(
    price,
):

    if (
        not trade.active
        or trade.tp2_done
    ):
        return

    trade.tp2_done = True

    trade.remaining_percent -= (
        TP2_PERCENT
    )

    print(
        f"TP2: closed "
        f"{TP2_PERCENT}% "
        f"at {price}"
        f" | remaining "
        f"{trade.remaining_percent}%"
    )

    trade.trailing_active = True

    trade.trailing_peak = D(
        price
    )

    print(
        "TRAILING ACTIVATED "
        f"for final "
        f"{trade.remaining_percent}% "
        f"| distance "
        f"{TRAILING_DISTANCE_PERCENT}%"
    )


def update_trailing(
    price,
):

    if (
        not trade.active
        or not trade.trailing_active
    ):

        return False

    price = D(
        price
    )

    if trade.direction == "LONG":

        if (
            trade.trailing_peak is None
            or price
            > trade.trailing_peak
        ):

            trade.trailing_peak = (
                price
            )

        trigger = (
            trade.trailing_peak
            * (
                Decimal("1")
                -
                TRAILING_DISTANCE_PERCENT
                / Decimal("100")
            )
        )

        if price <= trigger:

            trailing_exit(
                price
            )

            return True

    else:

        if (
            trade.trailing_peak is None
            or price
            < trade.trailing_peak
        ):

            trade.trailing_peak = (
                price
            )

        trigger = (
            trade.trailing_peak
            * (
                Decimal("1")
                +
                TRAILING_DISTANCE_PERCENT
                / Decimal("100")
            )
        )

        if price >= trigger:

            trailing_exit(
                price
            )

            return True

    return False


def trailing_exit(
    price,
):

    remaining = (
        trade.remaining_percent
    )

    trade.remaining_percent = (
        Decimal("0")
    )

    print(
        f"TRAIL EXIT: closed "
        f"{remaining}% "
        f"at {price}"
        " | remaining 0%"
    )

    cleanup_trade()


def cleanup_trade():

    if IDLE_PYRAMID_CLEANUP:

        trade.pyramids = 0

        print(
            "IDLE PYRAMID CLEANUP: "
            "COMPLETE"
        )

    trade.reset()

    print(
        "TRADE STATE RESET: COMPLETE"
    )


# ============================================================
# 0F-4F SAFE BRIDGE TEST
# ============================================================

async def run_0f4f_test():

    print(
        "=" * 60
    )

    print(
        "0F-4F SAFE ORDER BRIDGE TEST"
    )

    print(
        "NO LIVE ORDERS WILL BE SENT"
    )

    print(
        "=" * 60
    )

    start_simulated_trade(
        "LONG",
        Decimal("100.00"),
    )

    print(
        "SIM PRICE: 100.31"
    )

    add_pyramid(
        Decimal("100.31")
    )

    print(
        "SIM PRICE: 100.82"
    )

    take_profit_1(
        Decimal("100.82")
    )

    print(
        "SIM PRICE: 101.35"
    )

    take_profit_2(
        Decimal("101.35")
    )

    print(
        "SIM PRICE: 101.70"
    )

    update_trailing(
        Decimal("101.70")
    )

    print(
        "SIM PRICE: 101.80"
    )

    update_trailing(
        Decimal("101.80")
    )

    print(
        "SIM PRICE: 101.55"
    )

    update_trailing(
        Decimal("101.55")
    )

    # ========================================================
    # ORDER BRIDGE VALIDATION
    # ========================================================

    bridge_passed = (
        await order_bridge(
            direction="LONG",
            quantity=Decimal(
                "0.001"
            ),
            purpose="test",
        )
    )

    print(
        "=" * 60
    )

    if bridge_passed:

        print(
            "0F-4F ORDER VALIDATION: "
            "PASSED"
        )

    elif not weex_credentials_ready():

        print(
            "0F-4F ORDER VALIDATION: "
            "WAITING FOR API CREDENTIALS"
        )

    else:

        print(
            "0F-4F ORDER BRIDGE: "
            "SAFELY BLOCKED"
        )

    print(
        "NO LIVE ORDER WAS SENT"
    )

    print(
        "=" * 60
    )

    await send_telegram(
        "🧪 MODULE 0F-4F TEST\n"
        f"{SYMBOL}\n\n"
        "✅ Trade lifecycle engine\n"
        "✅ Order payload builder\n"
        "✅ Order validation\n"
        "✅ Unique client order IDs\n"
        "✅ Anti-duplicate protection\n"
        "🛡 Hard execution lock active\n"
        "⚠️ No live order was sent."
    )


# ============================================================
# WEBSOCKET MESSAGE PARSER
# ============================================================

def extract_price(
    message,
):

    try:

        data = json.loads(
            message
        )

    except Exception:

        return None, None

    # WEEX V3 server ping
    if (
        data.get("event")
        == "ping"
        or data.get("type")
        == "ping"
    ):

        return "PING", None

    # Subscription confirmation
    if (
        data.get("result")
        is True
    ):

        return "SUBSCRIBED", None

    candidates = []

    payload = data.get(
        "data"
    )

    if isinstance(
        payload,
        dict,
    ):

        candidates.append(
            payload
        )

    elif isinstance(
        payload,
        list,
    ):

        candidates.extend(
            x
            for x in payload
            if isinstance(
                x,
                dict,
            )
        )

    candidates.append(
        data
    )

    fields = (
        "close",
        "c",
        "price",
        "lastPrice",
        "last",
    )

    for item in candidates:

        for field in fields:

            if field not in item:
                continue

            price = D(
                item.get(
                    field
                )
            )

            if (
                price is not None
                and price > 0
            ):

                return (
                    "PRICE",
                    price,
                )

    return None, None


# ============================================================
# STABILIZED WEEX WEBSOCKET
# ============================================================

async def monitor_weex():

    reconnect_delay = (
        RECONNECT_DELAY_SECONDS
    )

    while True:

        try:

            print(
                "CONNECTING TO WEEX..."
            )

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent":
                    "WEEX-0F-4F-Bot/1.0"
                },
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
            ) as ws:

                print(
                    "CONNECTED TO WEEX"
                )

                subscribe = {
                    "method":
                    "SUBSCRIBE",

                    "params": [
                        SUBSCRIPTION_CHANNEL
                    ],

                    "id": 1,
                }

                await ws.send(
                    json.dumps(
                        subscribe
                    )
                )

                print(
                    "SUBSCRIBED TO "
                    f"{SUBSCRIPTION_CHANNEL}"
                )

                reconnect_delay = (
                    RECONNECT_DELAY_SECONDS
                )

                async for message in ws:

                    kind, price = (
                        extract_price(
                            message
                        )
                    )

                    if kind == "PING":

                        # Exact V3 application
                        # PONG recommended by WEEX.
                        await ws.send(
                            json.dumps(
                                {
                                    "method":
                                    "PONG",

                                    "id": 1,
                                }
                            )
                        )

                        continue

                    if (
                        kind
                        == "SUBSCRIBED"
                    ):

                        print(
                            "SUBSCRIPTION "
                            "CONFIRMED"
                        )

                        continue

                    if kind == "PRICE":

                        print(
                            f"{SYMBOL} PRICE: "
                            f"{price}"
                        )

        except asyncio.CancelledError:

            raise

        except Exception as exc:

            print(
                "WEEX CONNECTION ERROR:",
                exc,
            )

            print(
                "RECONNECTING IN "
                f"{reconnect_delay}s..."
            )

            await asyncio.sleep(
                reconnect_delay
            )

            reconnect_delay = min(
                reconnect_delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


# ============================================================
# STARTUP
# ============================================================

async def startup_message():

    credential_status = (
        "READY"
        if weex_credentials_ready()
        else "MISSING"
    )

    print(
        "=" * 60
    )

    print(
        "MODULE 0F-4F STARTING"
    )

    print(
        f"{SYMBOL} SAFE "
        "LIVE-ORDER BRIDGE"
    )

    print(
        "=" * 60
    )

    print(
        "Entry:",
        f"{INITIAL_ENTRY_PERCENT}%"
    )

    print(
        "Leverage:",
        f"{LEVERAGE}x"
    )

    print(
        "Max Leverage:",
        f"{MAX_LEVERAGE}x"
    )

    print(
        "Max Pyramids:",
        MAX_PYRAMID_ADDS,
    )

    print(
        "Max Backups:",
        MAX_BACKUPS,
    )

    print(
        "Max Fund Exposure:",
        f"{MAX_FUND_EXPOSURE_PERCENT}%"
    )

    print(
        "TP1 / TP2 / TP3:",
        f"{TP1_PERCENT}% / "
        f"{TP2_PERCENT}% / "
        f"{TP3_PERCENT}%"
    )

    print(
        "Trailing Distance:",
        f"{TRAILING_DISTANCE_PERCENT}%"
    )

    print(
        "WEEX API CREDENTIALS:",
        credential_status,
    )

    print(
        "ORDER BRIDGE: "
        "VALIDATION MODE"
    )

    print(
        "ANTI-DUPLICATE ORDERS: "
        "ACTIVE"
    )

    print(
        "HARD SAFETY LOCK: ACTIVE"
    )

    print(
        "LIVE ORDER EXECUTION: "
        "DISABLED"
    )

    print(
        "=" * 60
    )

    await send_telegram(
        "✅ MODULE 0F-4F ONLINE\n"
        f"{SYMBOL}\n\n"
        "Safe Live-Order Bridge\n"
        f"WEEX credentials: "
        f"{credential_status}\n"
        "✅ Order validation active\n"
        "✅ Anti-duplicate protection\n"
        "🛡 Hard execution lock active\n"
        "⚠️ Live order execution disabled"
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    await startup_message()

    await run_0f4f_test()

    print(
        "LIVE MARKET MONITORING ACTIVE"
    )

    print(
        "WAITING FOR WEEX "
        "MARKET DATA..."
    )

    await monitor_weex()


if __name__ == "__main__":

    asyncio.run(
        main())
