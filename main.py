import asyncio
import json
import websockets
from telegram import Bot

# ==========================
# Telegram Settings
# ==========================

TOKEN = "8684817654:AAG48fn13BtVazkR9dCIneC_dItUFUxrXAU"
CHAT_ID = "8587384068"

bot = Bot(token=TOKEN)

# ==========================
# WEEX Settings
# ==========================

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
            print("Connecting to WEEX...")

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "Python"
                },
                ping_interval=20,
                ping_timeout=20
            ) as ws:

                print("CONNECTED")
                await send("✅ CONNECTED to WEEX WebSocket")

                # Subscribe
                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))
                print("Subscription sent:")
                print(json.dumps(SUBSCRIBE_MESSAGE))

                await send("📡 Subscription sent.")

                while True:
                    message = await ws.recv()

                    print("===================================")
                    print("RAW MESSAGE:")
                    print(message)
                    print("===================================")

                    # Forward raw message to Telegram
                    await send(f"📩 {message}")

                    # Try decoding JSON
                    try:
                        data = json.loads(message)
                    except Exception:
                        continue

                    # Respond to ping if required
                    if isinstance(data, dict):

                        if "ping" in data:
                            pong = {"pong": data["ping"]}
                            await ws.send(json.dumps(pong))
                            print("Sent pong:", pong)

                        elif data.get("op") == "ping":
                            await ws.send(json.dumps({"op": "pong"}))
                            print("Sent op pong")

        except Exception as e:
            print("Connection Error:", e)

            await send(f"❌ Connection Error:\n{e}")

            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(connect())
