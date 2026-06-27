import asyncio
import json
import websockets
from telegram import Bot

# Telegram settings
TOKEN = "8684817654:AAG48fn13BtVazkR9dCIneC_dItUFUxrXAU"
CHAT_ID = "8587384068"

bot = Bot(token=TOKEN)

# WEEX WebSocket
WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIBE_MESSAGE = {
    "op": "subscribe",
    "args": [
        "ticker.BTCUSDT"
    ]
}


async def send(text):
    """Send a Telegram message."""
    try:
        if len(text) > 3900:
            text = text[:3900] + "\n...(truncated)"
        await bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print("Telegram Error:", e)


async def connect():
    while True:
        try:
            async with websockets.connect(
                WS_URL,
                additional_headers={"User-Agent": "Python"}
            ) as ws:

                print("CONNECTED")
                await send("✅ CONNECTED to WEEX WebSocket")

                # Subscribe to ticker
                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))
                print("Subscription sent.")
                await send("📡 Subscription sent.")

                while True:
                    message = await ws.recv()

                    print("RECEIVED:", message)

                    await send(f"📩 {message}")

        except Exception as e:
            print("Connection Error:", e)
            await send(f"❌ Connection Error:\n{e}")

            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


asyncio.run(connect())
