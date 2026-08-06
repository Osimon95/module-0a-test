import asyncio
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import websockets
from telegram import Bot

# ============================================================
# CONFIGURATION
# ============================================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"
SYMBOL = "BTCUSDT"
SUBSCRIPTION_CHANNEL = f"{SYMBOL}@ticker"

# Read values from Render Environment Variables.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Decimal("0") sends an alert for every actual price change.
MINIMUM_PERCENT_CHANGE = Decimal(
    os.getenv("MINIMUM_PERCENT_CHANGE", "0")
)

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


def telegram_is_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def display_telegram_status() -> None:
    if telegram_is_configured():
        print("TELEGRAM CONFIG: READY", flush=True)
    else:
        print(
            "TELEGRAM CONFIG: MISSING. "
            "Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.",
            flush=True,
        )


async def send_telegram(bot: Optional[Bot], message: str) -> None:
    """Send a Telegram message without stopping the price monitor."""

    if bot is None or not telegram_is_configured():
        print(
            "TELEGRAM WARNING: Token or chat ID is missing.",
            flush=True,
        )
        return

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        print("TELEGRAM MESSAGE SENT", flush=True)

    except Exception as error:
        print(
            f"TELEGRAM ERROR: {type(error).__name__}: {error}",
            flush=True,
        )
def display_telegram_status() -> None:
    if telegram_is_configured():
        print("TELEGRAM CONFIG: READY", flush=True)
    else:
        print(
            "TELEGRAM CONFIG: MISSING. "
            "Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.",
            flush=True,
        )
async def send_telegram(bot: Optional[Bot], message: str) -> None:
    """Send a Telegram message without stopping the price monitor."""

    if bot is None or not telegram_is_configured():
        print(
            "TELEGRAM WARNING: Token or chat ID is missing.",
            flush=True,
        )
        return

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        print("TELEGRAM MESSAGE SENT", flush=True)

    except Exception as error:
        print(
            f"TELEGRAM ERROR: {type(error).__name__}: {error}",
            flush=True,
        )


def convert_to_price(value: Any) -> Optional[Decimal]:
    """Convert a possible ticker value into a valid positive price."""

    if value is None or isinstance(value, bool):
        return None

    try:
        price = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None

    if not price.is_finite() or price <= 0:
        return None

    return price


def search_price(data: Any) -> Optional[Decimal]:
    """Search a WEEX response for the most likely current price."""

    preferred_keys = (
        "last",
        "lastPrice",
        "last_price",
        "close",
        "price",
        "markPrice",
        "mark_price",
    )

    if isinstance(data, dict):
        for key in preferred_keys:
            if key in data:
                price = convert_to_price(data.get(key))
                if price is not None:
                    return price

        nested_keys = (
            "data",
            "result",
            "ticker",
            "tick",
        )

        for key in nested_keys:
            if key in data:
                price = search_price(data.get(key))
                if price is not None:
                    return price

        for value in data.values():
            if isinstance(value, (dict, list)):
                price = search_price(value)
                if price is not None:
                    return price

    elif isinstance(data, list):
        for item in data:
            price = search_price(item)
            if price is not None:
                return price

    return None
def calculate_percentage_change(
    old_price: Decimal,
    new_price: Decimal,
) -> Decimal:
    if old_price <= 0:
        return Decimal("0")

    return ((new_price - old_price) / old_price) * Decimal("100")


def format_decimal(value: Decimal, places: int = 4) -> str:
    formatted = f"{value:.{places}f}"
    return formatted.rstrip("0").rstrip(".")


def is_subscription_confirmation(data: Any) -> bool:
    if not isinstance(data, dict):
        return False

    message_text = json.dumps(data).lower()

    return any(
        phrase in message_text
        for phrase in (
            "subscribe",
            "subscribed",
            "subscription",
        )
    ) and not search_price(data)


async def handle_application_ping(
    websocket: Any,
    data: Any,
) -> bool:
    """Respond to WEEX application-level ping messages."""

    if isinstance(data, str):
        if data.lower() == "ping":
            await websocket.send("pong")
            print("APPLICATION PONG SENT", flush=True)
            return True

        return False

    if not isinstance(data, dict):
        return False

    if "ping" in data:
        ping_value = data.get("ping")

        pong_message = {
            "pong": ping_value,
        }

        await websocket.send(json.dumps(pong_message))
        print("APPLICATION PONG SENT", flush=True)
        return True

    event = str(data.get("event", "")).lower()
    method = str(data.get("method", "")).lower()

    if event == "ping" or method == "ping":
        pong_message = {
            "method": "PONG",
            "id": data.get("id", 1),
        }

        await websocket.send(json.dumps(pong_message))
        print("APPLICATION PONG SENT", flush=True)
        return True

    return False


async def monitor_prices(bot: Optional[Bot]) -> None:
    previous_price: Optional[Decimal] = None

    async with websockets.connect(
        WS_URL,
        additional_headers={
            "User-Agent": "WEEX-BTC-Price-Bot/1.0",
        },
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10,
        open_timeout=20,
    ) as websocket:

        print("CONNECTED TO WEEX", flush=True)

        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [
                SUBSCRIPTION_CHANNEL,
            ],
            "id": 1,
        }

        await websocket.send(json.dumps(subscribe_message))

        print(
            f"SUBSCRIBED TO {SUBSCRIPTION_CHANNEL}",
            flush=True,
        )

        await send_telegram(
            bot,
            f"✅ WEEX bot connected\nWatching {SYMBOL}",
        )
    while True:
            raw_message = await websocket.recv()

            try:
                data = json.loads(raw_message)
            except (json.JSONDecodeError, TypeError):
                data = raw_message

            if await handle_application_ping(websocket, data):
                continue

            if is_subscription_confirmation(data):
                print("SUBSCRIPTION CONFIRMED", flush=True)
                continue

            current_price = search_price(data)

            if current_price is None:
                continue

            if previous_price is None:
                previous_price = current_price

                print(
                    f"{SYMBOL} INITIAL PRICE: "
                    f"{format_decimal(current_price)}",
                    flush=True,
                )

                await send_telegram(
                    bot,
                    f"📈 {SYMBOL} initial price: "
                    f"{format_decimal(current_price)}",
                )
                continue

            if current_price == previous_price:
                continue

            percentage_change = calculate_percentage_change(
                previous_price,
                current_price,
            )

            print(
                f"{SYMBOL} PRICE: {format_decimal(current_price)} | "
                f"CHANGE: {percentage_change:+.6f}%",
                flush=True,
            )

            if abs(percentage_change) >= MINIMUM_PERCENT_CHANGE:
                direction = "🟢 UP" if percentage_change > 0 else "🔴 DOWN"

                telegram_message = (
                    f"{direction}\n"
                    f"Symbol: {SYMBOL}\n"
                    f"Previous: {format_decimal(previous_price)}\n"
                    f"Current: {format_decimal(current_price)}\n"
                    f"Change: {percentage_change:+.6f}%"
                )

                await send_telegram(
                    bot,
                    telegram_message,
                )

            previous_price = current_price


async def main() -> None:
    display_telegram_status()

    bot: Optional[Bot] = None

    if telegram_is_configured():
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

    reconnect_delay = RECONNECT_DELAY_SECONDS

    while True:
        try:
            await monitor_prices(bot)
            reconnect_delay = RECONNECT_DELAY_SECONDS

        except asyncio.CancelledError:
            print("BOT STOPPED", flush=True)
            raise

        except KeyboardInterrupt:
            print("BOT STOPPED BY USER", flush=True)
            return

        except Exception as error:
            print(
                f"CONNECTION ERROR: "
                f"{type(error).__name__}: {error}",
                flush=True,
            )

            print(
                f"RECONNECTING IN {reconnect_delay} SECONDS",
                flush=True,
            )

            await asyncio.sleep(reconnect_delay)

            reconnect_delay = min(
                reconnect_delay * 2,
                MAX_RECONNECT_DELAY_SECONDS,
            )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("APPLICATION CLOSED", flush=True)
