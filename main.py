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

# Temporary hard-coded Telegram details.
# Paste your existing token and chat ID between the normal quotation marks.
TELEGRAM_BOT_TOKEN = os.getenv(
    "8684817654:AAGI7l96augCUlSaBx1xEReq7AZFfQtJhZc",
    "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE",
)

TELEGRAM_CHAT_ID = os.getenv(
    "8587384068",
    "PASTE_YOUR_TELEGRAM_CHAT_ID_HERE",
)

# Send on every actual price change.
# No 60-second timer is used.
MINIMUM_PERCENT_CHANGE = Decimal("0")

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60

# =====================================
# Telegram Settings
# =====================================

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    print("TELEGRAM CONFIG: LOADED", flush=True)
else:
    print("TELEGRAM CONFIG: MISSING", flush=True)
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


# ============================================================
# PRICE EXTRACTION
# ============================================================

def convert_to_price(value: Any) -> Optional[Decimal]:
    """Convert a possible price value to a valid positive Decimal."""
    if value is None or isinstance(value, bool):
        return None

    try:
        price = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None

    if not price.is_finite():
        return None

    if price <= 0:
        return None

    return price


def extract_price(payload: Any) -> Optional[Decimal]:
    """
    Extract the latest traded price from possible WEEX message formats.

    Only recognised ticker price fields are used, preventing values such
    as volume, timestamps, bid quantity or subscription IDs from being
    mistaken for the BTC price.
    """
    price_keys = (
        "lastPrice",
        "last_price",
        "last",
        "close",
        "price",
        "markPrice",
        "mark_price",
    )

    if isinstance(payload, dict):
        # Check recognised price fields at the current level.
        for key in price_keys:
            if key in payload:
                price = convert_to_price(payload.get(key))

                if price is not None:
                    return price

        # Check the common nested WEEX data containers.
        for key in ("data", "result", "ticker"):
            if key in payload:
                price = extract_price(payload.get(key))

                if price is not None:
                    return price

    elif isinstance(payload, list):
        for item in payload:
            price = extract_price(item)

            if price is not None:
                return price

    return None


# ============================================================
# PERCENTAGE CALCULATION
# ============================================================

def calculate_percentage_change(
    old_price: Decimal,
    new_price: Decimal,
) -> Decimal:
    """Calculate the percentage change from old price to new price."""
    if old_price <= 0:
        return Decimal("0")

    return ((new_price - old_price) / old_price) * Decimal("100")


def format_price(price: Decimal) -> str:
    """Format price without unnecessary trailing zeros."""
    formatted = format(price, "f")

    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")

    return formatted


def create_price_message(
    previous_price: Decimal,
    current_price: Decimal,
    percentage_change: Decimal,
) -> str:
    """Create the Telegram price-change message."""
    price_difference = current_price - previous_price

    if percentage_change > 0:
        direction = "🟢 UP"
        sign = "+"
    elif percentage_change < 0:
        direction = "🔴 DOWN"
        sign = ""
    else:
        direction = "⚪ UNCHANGED"
        sign = ""

    return (
        f"📈 {SYMBOL} PRICE CHANGE\n\n"
        f"Previous: {format_price(previous_price)}\n"
        f"Current: {format_price(current_price)}\n"
        f"Difference: {format_price(price_difference)}\n"
        f"Change: {sign}{percentage_change:.6f}%\n"
        f"Direction: {direction}"
    )


# ============================================================
# WEEX WEBSOCKET
# ============================================================

async def handle_application_ping(
    websocket: Any,
    data: Any,
) -> bool:
    """Respond to possible WEEX application-level ping messages."""
    if not isinstance(data, dict):
        return False

    if data.get("event") == "ping":
        await websocket.send(
            json.dumps(
                {
                    "method": "PONG",
                    "id": data.get("id", 1),
                }
            )
        )

        print("APPLICATION PONG SENT", flush=True)
        return True

    if data.get("method") == "PING":
        await websocket.send(
            json.dumps(
                {
                    "method": "PONG",
                    "id": data.get("id", 1),
                }
            )
        )

        print("APPLICATION PONG SENT", flush=True)
        return True

    if "ping" in data:
        await websocket.send(
            json.dumps(
                {
                    "pong": data.get("ping"),
                }
            )
        )

        print("APPLICATION PONG SENT", flush=True)
        return True

    return False


async def watch_prices(bot: Bot) -> None:
    """Connect to WEEX and watch BTCUSDT prices."""
    previous_price: Optional[Decimal] = None

    async with websockets.connect(
        WS_URL,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10,
        open_timeout=20,
    ) as websocket:
        print("CONNECTED TO WEEX", flush=True)

        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": [SUBSCRIPTION_CHANNEL],
            "id": 1,
        }

        await websocket.send(json.dumps(subscribe_message))

        print(
            f"SUBSCRIBED TO {SUBSCRIPTION_CHANNEL}",
            flush=True,
        )

        await send_telegram(
            bot,
            "✅ WEEX bot connected\n"
            f"Watching {SYMBOL}\n"
            "Alert mode: every valid price change",
        )

        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                print(
                    f"IGNORED NON-JSON MESSAGE: {raw_message}",
                    flush=True,
                )
                continue

            if await handle_application_ping(websocket, data):
                continue

            # Subscription acknowledgement.
            if isinstance(data, dict):
                if (
                    data.get("id") == 1
                    and "data" not in data
                    and "result" in data
                ):
                    print(
                        "SUBSCRIPTION CONFIRMED",
                        flush=True,
                    )
                    continue

            current_price = extract_price(data)

            if current_price is None:
                continue

            # Ignore zero, negative and invalid prices.
            if current_price <= 0:
                continue

            # First valid price becomes the starting reference.
            if previous_price is None:
                previous_price = current_price

                print(
                    f"{SYMBOL} INITIAL PRICE: "
                    f"{format_price(current_price)}",
                    flush=True,
                )

                await send_telegram(
                    bot,
                    f"📈 {SYMBOL} starting price: "
                    f"{format_price(current_price)}",
                )

                continue

            # Ignore duplicate ticker messages.
            if current_price == previous_price:
                continue

            percentage_change = calculate_percentage_change(
                previous_price,
                current_price,
            )

            print(
                f"{SYMBOL} PRICE: {format_price(current_price)} | "
                f"CHANGE: {percentage_change:+.6f}%",
                flush=True,
            )

            # MINIMUM_PERCENT_CHANGE is currently zero, so every
            # genuine price change triggers a Telegram message.
            if abs(percentage_change) >= MINIMUM_PERCENT_CHANGE:
                message = create_price_message(
                    previous_price=previous_price,
                    current_price=current_price,
                    percentage_change=percentage_change,
                )

                await send_telegram(bot, message)

            previous_price = current_price


# ============================================================
# MAIN RECONNECT LOOP
# ============================================================

async def main() -> None:
    """Run the WEEX bot and reconnect automatically if disconnected."""
    print(
        "TELEGRAM CONFIG: "
        f"{'READY' if telegram_is_configured() else 'MISSING'}",
        flush=True,
    )

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    reconnect_delay = RECONNECT_DELAY_SECONDS

    while True:
        try:
            await watch_prices(bot)

            # Reset reconnect delay after a successful connection.
            reconnect_delay = RECONNECT_DELAY_SECONDS

        except asyncio.CancelledError:
            print("BOT STOPPED", flush=True)
            raise

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
        print("BOT STOPPED BY USER", flush=True)
