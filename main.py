import asyncio
import json
import os

import websockets
from telegram import Bot


# =====================================
# Settings
# =====================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

# Add these as Environment Variables on Render
TELEGRAM_BOT_TOKEN = os.getenv("8684817654:AAG48fn13BtVazkR9dCIneC_dItUFUxrXAU")
TELEGRAM_CHAT_ID = os.getenv("8587384068")


async def send_telegram(bot: Bot, message: str) -> None:
    """Send a Telegram message without crashing the WebSocket bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(
            "TELEGRAM ERROR: TELEGRAM_BOT_TOKEN or "
            "TELEGRAM_CHAT_ID is missing",
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


async def main():
    if not TELEGRAM_BOT_TOKEN:
        print(
            "WARNING: TELEGRAM_BOT_TOKEN is not configured",
            flush=True,
        )

    bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

    while True:
        try:
            print("CONNECTING TO WEEX...", flush=True)

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "WEEX-BTC-Bot/1.0"
                },
                open_timeout=20,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10,
            ) as ws:

                print("CONNECTED", flush=True)

                if bot:
                    await send_telegram(
                        bot,
                        "✅ Connected to WEEX WebSocket",
                    )

                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        "BTCUSDT@ticker"
                    ],
                    "id": 1,
                }

                await ws.send(json.dumps(subscribe_message))
                print("SUBSCRIPTION SENT", flush=True)

                while True:
                    message = await ws.recv()

                    try:
                        data = json.loads(message)

                    except json.JSONDecodeError:
                        print(
                            f"NON-JSON MESSAGE: {message}",
                            flush=True,
                        )
                        continue

                    # WEEX application-level ping
                    if data.get("event") == "ping":
                        pong_message = {
                            "method": "PONG",
                            "id": 1,
                        }

                        await ws.send(json.dumps(pong_message))
                        print("PONG SENT", flush=True)
                        continue

                    # Subscription acknowledgement
                    if "result" in data:
                        if data.get("result") is True:
                            print("SUBSCRIBED", flush=True)

                            if bot:
                                await send_telegram(
                                    bot,
                                    "📡 Subscribed to BTCUSDT ticker",
                                )
                        else:
                            error_message = data.get("msg", data)

                            print(
                                f"SUBSCRIPTION ERROR: {error_message}",
                                flush=True,
                            )

                            if bot:
                                await send_telegram(
                                    bot,
                                    "❌ WEEX subscription error:\n"
                                    f"{error_message}",
                                )

                        continue

                    # Ticker update
                    if data.get("e") == "ticker":
                        ticker_list = data.get("d", [])

                        if isinstance(ticker_list, list):
                            for ticker in ticker_list:
                                if not isinstance(ticker, dict):
                                    continue

                                price = ticker.get("c")

                                if price is not None:
                                    print(
                                        f"BTCUSDT PRICE: {price}",
                                        flush=True,
                                    )

                        continue

                    print(
                        f"OTHER MESSAGE: {data}",
                        flush=True,
                    )

        except asyncio.CancelledError:
            raise

        except websockets.ConnectionClosed as error:
            error_text = (
                f"WEEX disconnected: "
                f"code={error.code}, reason={error.reason}"
            )

            print(error_text, flush=True)

            if bot:
                await send_telegram(
                    bot,
                    f"⚠️ {error_text}\nReconnecting in 5 seconds...",
                )

        except Exception as error:
            error_text = (
                f"{type(error).__name__}: {error}"
            )

            print(
                f"CONNECTION ERROR: {error_text}",
                flush=True,
            )

            if bot:
                await send_telegram(
                    bot,
                    "❌ WEEX connection error:\n"
                    f"{error_text}\n\n"
                    "Reconnecting in 5 seconds...",
                )

        print("RECONNECTING IN 5 SECONDS...", flush=True)
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("STOPPED", flush=True)
