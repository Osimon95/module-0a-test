import os
import json
import asyncio
import websockets
from telegram import Bot

# ==========================
# Configuration
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIBE_MESSAGE = {
    "op": "subscribe",
    "args": [
        "ticker.BTCUSDT"
    ]
}


# ==========================
# Telegram
# ==========================

async def send(text):
    try:
        if len(text) > 3900:
            text = text[:3900] + "\n...(truncated)"

        await bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )

    except Exception as e:
        print("Telegram Error:", e)


# ==========================
# WebSocket
# ==========================

async def websocket_loop():

    while True:

        try:

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "Python"
                },
                ping_interval=20,
                ping_timeout=20
            ) as ws:

                print("CONNECTED TO WEEX")
                await send("✅ CONNECTED TO WEEX")

                # Subscribe
                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))
                print("SUBSCRIBED")
                await send("📡 SUBSCRIBED")

                while True:

                    message = await ws.recv()

                    print(message)

                    await send(message)

        except Exception as e:

            print("WEBSOCKET ERROR:", e)

            await send(f"❌ ERROR:\n{e}")

            await asyncio.sleep(5)


# ==========================
# Main
# ==========================

async def main():
    await websocket_loop()


if __name__ == "__main__":
    asyncio.run(main())
