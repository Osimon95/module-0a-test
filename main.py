import asyncio
import json
import os
import time
from typing import Any, Optional

import websockets
from telegram import Bot

# =====================================
# Settings
# =====================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"
SYMBOL = os.getenv("SYMBOL", "BTCUSDT").upper()

TELEGRAM_BOT_TOKEN = "8684817654:AAGI7l96augCUlSaBx1xEReq7AZFfQtJhZc”
TELEGRAM_CHAT_ID = "8587384068"
print("TELEGRAM CONFIG: USING HARD-CODED VALUES", flush=True)


# Send Telegram updates at most once every 60 seconds.
# Set this to 0 to send every price change.
TELEGRAM_PRICE_INTERVAL_SECONDS = int(
    os.getenv("TELEGRAM_PRICE_INTERVAL_SECONDS", "60")
)

RECONNECT_DELAY_SECONDS = 5
MAX_RECONNECT_DELAY_SECONDS = 60


def extract_price(message: dict[str, Any]) -> Optional[float]:
    """Extract the latest traded price from a WEEX ticker message."""

    if message.get("e") != "ticker":
        return None

    if message.get("s") != SYMBOL:
        return None

    ticker_data = message.get("d")

    if not isinstance(ticker_data, list) or not ticker_data:
        return None

    ticker = ticker_data[0]

    if not isinstance(ticker, dict):
        return None

    # Latest traded price
    raw_price = ticker.get("c")

    try:
        price = float(raw_price)
    except (TypeError, ValueError):
        return None

    # Ignore invalid prices
    if price <= 0:
        return None

    return price


async def send_telegram(bot: Optional[Bot], message: str):

    if bot is None:
        return

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )

        print("TELEGRAM MESSAGE SENT", flush=True)

    except Exception as error:
        print(f"TELEGRAM ERROR: {error}", flush=True)
async def stream_prices(bot: Optional[Bot]) -> None:
    """Connect to WEEX, subscribe, and process valid ticker updates."""

    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [f"{SYMBOL}@ticker"],
        "id": 1,
    }

    last_price: Optional[float] = None
    last_telegram_time = 0.0

    async with websockets.connect(
        WS_URL,
        additional_headers={
            "User-Agent": "WEEX-BTC-Bot/1.0"
        },
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10,
        open_timeout=20,
    ) as ws:

        print("CONNECTED TO WEEX", flush=True)

        await ws.send(json.dumps(subscribe_message))

        print(
            f"SUBSCRIBED TO {SYMBOL}@ticker",
            flush=True,
        )

        await send_telegram(
            bot,
            f"✅ WEEX bot connected\nWatching {SYMBOL}",
        )

        while True:
            raw_message = await ws.recv()

            try:
                data = json.loads(raw_message)
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(data, dict):
                continue

            # WEEX application-level ping
            if (
                data.get("event") == "ping"
                or data.get("type") == "ping"
            ):
                pong_message = {
                    "method": "PONG",
                    "id": 1,
                }

                await ws.send(
                    json.dumps(pong_message)
                )

                continue

            # Subscription acknowledgement
            if data.get("id") == 1 and "result" in data:

                if data.get("result") is True:
                    print(
                        "SUBSCRIPTION CONFIRMED",
                        flush=True,
                    )
                else:
                    raise RuntimeError(
                        "WEEX subscription failed: "
                        f"{data.get('msg', data)}"
                    )

                continue

            price = extract_price(data)

            if price is None:
                continue

            # Ignore repeated prices
            if price == last_price:
                continue

            last_price = price

            print(
                f"{SYMBOL} PRICE: {price}",
                flush=True,
            )

            now = time.monotonic()

            interval_elapsed = (
                now - last_telegram_time
                >= TELEGRAM_PRICE_INTERVAL_SECONDS
            )

            if (
                TELEGRAM_PRICE_INTERVAL_SECONDS == 0
                or interval_elapsed
            ):
                await send_telegram(
                    bot,
                    f"📈 {SYMBOL} price: {price}",
                )

                last_telegram_time = now
async def main() -> None:
    """Run continuously and reconnect after connection failures."""

    bot: Optional[Bot] = None

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.initialize()
    else:
        print(
            "TELEGRAM WARNING: TELEGRAM_BOT_TOKEN or "
            "TELEGRAM_CHAT_ID is missing. "
            "Price logging will continue.",
            flush=True,
        )

    reconnect_delay = RECONNECT_DELAY_SECONDS

    try:
        while True:
            try:
                await stream_prices(bot)

                reconnect_delay = RECONNECT_DELAY_SECONDS

            except asyncio.CancelledError:
                raise

            except Exception as error:
                print(
                    f"CONNECTION ERROR: {error}",
                    flush=True,
                )

                await send_telegram(
                    bot,
                    (
                        f"⚠️ {SYMBOL} bot connection error\n"
                        f"{error}\n"
                        f"Reconnecting in "
                        f"{reconnect_delay} seconds."
                    ),
                )

                await asyncio.sleep(reconnect_delay)

                reconnect_delay = min(
                    reconnect_delay * 2,
                    MAX_RECONNECT_DELAY_SECONDS,
                )

    finally:
        if bot is not None:
            await bot.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("BOT STOPPED", flush=True)
