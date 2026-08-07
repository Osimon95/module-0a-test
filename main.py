import asyncio
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import websockets
from telegram import Bot


# ============================================================
# 0A — CONFIGURATION
# ============================================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SYMBOL = "BTCUSDT"
SUBSCRIPTION_CHANNEL = f"{SYMBOL}@ticker"


# Add these two values in Render Environment Variables:
#
# TELEGRAM_BOT_TOKEN
# TELEGRAM_CHAT_ID
#
# Do not put the actual token inside os.getenv().
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "",
).strip()


# Minimum percentage movement from the previous alert price.
#
# Examples:
# "0"   = notify on every actual price change
# "0.1" = notify after a 0.1% movement
# "0.5" = notify after a 0.5% movement
#
# You can add MINIMUM_PERCENT_CHANGE in Render.
MINIMUM_PERCENT_CHANGE = Decimal(
    os.getenv(
        "MINIMUM_PERCENT_CHANGE",
        "0",
    )
)


RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


# Prevent repeated Telegram connection messages after reconnection.
connection_notification_sent = False


# Price used for comparison.
last_alert_price: Optional[Decimal] = None
# ============================================================
# 0B — TELEGRAM AND PRICE FUNCTIONS
# ============================================================


def telegram_is_configured() -> bool:
    """Return True when both Telegram settings are available."""
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_CHAT_ID
    )


def display_telegram_status() -> None:
    """Show whether Telegram settings were loaded."""
    if telegram_is_configured():
        print(
            "TELEGRAM CONFIG: READY",
            flush=True,
        )
    else:
        print(
            "TELEGRAM CONFIG: MISSING. "
            "Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.",
            flush=True,
        )


async def send_telegram(
    bot: Bot,
    message: str,
) -> bool:
    """Send a Telegram message without stopping the price bot."""
    if not telegram_is_configured():
        print(
            "TELEGRAM WARNING: "
            "Token or chat ID is missing.",
            flush=True,
        )
        return False

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print(
            "TELEGRAM MESSAGE SENT",
            flush=True,
        )
        return True

    except Exception as error:
        print(
            "TELEGRAM ERROR: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )
        return False


def calculate_percentage_change(
    old_price: Decimal,
    new_price: Decimal,
) -> Decimal:
    """Calculate the absolute percentage movement."""
    if old_price <= 0:
        return Decimal("0")

    return abs(
        (new_price - old_price)
        / old_price
        * Decimal("100")
    )


def format_decimal(value: Decimal) -> str:
    """Format a decimal without unnecessary trailing zeroes."""
    text = format(value, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text
# ============================================================
# 0C — PRICE PROCESSING
# ============================================================


async def process_price(
    bot: Bot,
    price: Decimal,
) -> None:
    """Process a valid price and send percentage-based alerts."""
    global last_alert_price

    if price <= 0:
        return

    print(
        f"{SYMBOL} PRICE: {format_decimal(price)}",
        flush=True,
    )

    # First valid price becomes the starting comparison price.
    if last_alert_price is None:
        last_alert_price = price

        await send_telegram(
            bot,
            f"📈 {SYMBOL} starting price: "
            f"{format_decimal(price)}",
        )
        return

    # Ignore duplicate prices.
    if price == last_alert_price:
        return

    percentage_change = calculate_percentage_change(
        last_alert_price,
        price,
    )

    # Do not alert until the configured percentage is reached.
    if percentage_change < MINIMUM_PERCENT_CHANGE:
        return

    direction = "🟢 UP" if price > last_alert_price else "🔴 DOWN"

    previous_price = last_alert_price

    message = (
        f"{direction}\n"
        f"{SYMBOL}\n"
        f"Previous: {format_decimal(previous_price)}\n"
        f"Current: {format_decimal(price)}\n"
        f"Change: {format_decimal(percentage_change)}%"
    )

    message_sent = await send_telegram(
        bot,
        message,
    )

    # Update only after a successful message.
    # When Telegram is not configured, update it anyway to prevent
    # repeatedly processing the same accumulated movement.
    if message_sent or not telegram_is_configured():
        last_alert_price = price


def extract_price(data: Any) -> Optional[Decimal]:
    """Extract a valid ticker price from a WEEX message."""
    if not isinstance(data, dict):
        return None

    ticker_items = data.get("d")

    if not isinstance(ticker_items, list):
        return None

    if not ticker_items:
        return None

    first_ticker = ticker_items[0]

    if not isinstance(first_ticker, dict):
        return None

    price_text = first_ticker.get("c")

    if price_text in (None, ""):
        return None

    try:
        price = Decimal(str(price_text))
    except (InvalidOperation, ValueError, TypeError):
        return None

    if price <= 0:
        return None

    return price
# ============================================================
# 0D — WEEX CONNECTION AND APPLICATION STARTUP
# ============================================================


async def run_websocket(bot: Bot) -> None:
    """Connect to WEEX and automatically reconnect when necessary."""
    global connection_notification_sent

    reconnect_delay = RECONNECT_DELAY_SECONDS

    while True:
        try:
            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "WEEX-BTC-Bot/1.0",
                },
                ping_interval=None,
                ping_timeout=None,
                close_timeout=10,
            ) as websocket:

                print(
                    "CONNECTED TO WEEX",
                    flush=True,
                )

                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        SUBSCRIPTION_CHANNEL,
                    ],
                    "id": 1,
                }

                await websocket.send(
                    json.dumps(subscribe_message)
                )

                print(
                    f"SUBSCRIBED TO {SUBSCRIPTION_CHANNEL}",
                    flush=True,
                )

                # Send the connection notification only once
                # during the lifetime of this program.
                if not connection_notification_sent:
                    notification_sent = await send_telegram(
                        bot,
                        "✅ WEEX bot connected\n"
                        f"Watching {SYMBOL}",
                    )

                    if notification_sent:
                        connection_notification_sent = True

                # Reset the delay after a successful connection.
                reconnect_delay = RECONNECT_DELAY_SECONDS

                async for raw_message in websocket:
                    try:
                        data = json.loads(raw_message)
                    except (
                        json.JSONDecodeError,
                        TypeError,
                    ):
                        continue

                    if not isinstance(data, dict):
                        continue

                    # WEEX application-level ping.
                    if data.get("event") == "ping":
                        pong_message = {
                            "method": "PONG",
                            "id": 1,
                        }

                        await websocket.send(
                            json.dumps(pong_message)
                        )

                        print(
                            "APPLICATION PONG SENT",
                            flush=True,
                        )
                        continue

                    # Some WEEX messages may use a ping field.
                    if "ping" in data:
                        pong_message = {
                            "pong": data.get("ping"),
                        }

                        await websocket.send(
                            json.dumps(pong_message)
                        )

                        print(
                            "APPLICATION PONG SENT",
                            flush=True,
                        )
                        continue

                    # Subscription confirmation.
                    if data.get("result") is True:
                        print(
                            "SUBSCRIPTION CONFIRMED",
                            flush=True,
                        )
                        continue

                    # Ignore error responses but show them in logs.
                    if data.get("code") not in (None, 0, "0"):
                        print(
                            f"WEEX MESSAGE ERROR: {data}",
                            flush=True,
                        )
                        continue

                    # Process ticker updates.
                    if data.get("e") == "ticker":
                        price = extract_price(data)

                        if price is not None:
                            await process_price(
                                bot,
                                price,
                            )

        except websockets.exceptions.ConnectionClosedOK:
            print(
                "WEEX CLOSED CONNECTION NORMALLY",
                flush=True,
            )

        except websockets.exceptions.ConnectionClosedError as error:
            print(
                "WEEX CONNECTION CLOSED: "
                f"{error}",
                flush=True,
            )

        except asyncio.CancelledError:
            print(
                "APPLICATION STOPPED",
                flush=True,
            )
            raise

        except Exception as error:
            print(
                "CONNECTION ERROR: "
                f"{type(error).__name__}: {error}",
                flush=True,
            )

        print(
            f"RECONNECTING IN "
            f"{reconnect_delay} SECONDS",
            flush=True,
        )

        await asyncio.sleep(
            reconnect_delay
        )

        reconnect_delay = min(
            reconnect_delay * 2,
            MAX_RECONNECT_DELAY_SECONDS,
        )


async def main() -> None:
    """Start the Telegram and WEEX price-monitoring bot."""
    display_telegram_status()

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN
        if TELEGRAM_BOT_TOKEN
        else "TELEGRAM_TOKEN_NOT_CONFIGURED"
    )

    await run_websocket(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(
            "BOT STOPPED BY USER",
            flush=True,
