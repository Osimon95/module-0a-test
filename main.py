import asyncio
import json
from datetime import datetime

import websockets
from telegram import Bot

# =====================================
# Telegram Settings
# =====================================

TOKEN = "8684817654:AAG48fn13BtVazkR9dCIneC_dItUFUxrXAU"
CHAT_ID = "8587384068"

bot = Bot(token=TOKEN)

# =====================================
# WEEX Settings
# =====================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIBE_MESSAGE = {
    "op": "subscribe",
    "args": [
        "ticker.BTCUSDT"
    ]
}

# =====================================
# Helpers
# =====================================

def log(*args):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}]", *args)


async def send(text):
    """Send Telegram message safely."""
    try:
        if len(str(text)) > 3900:
            text = str(text)[:3900] + "\n...(truncated)"

        await bot.send_message(
            chat_id=CHAT_ID,
            text=str(text)
        )

    except Exception as e:
        log(f"Telegram Error: {e}")


# =====================================
# Main Connection
# =====================================

async def connect():
    while True:
        try:
            log("Connecting to WEEX...")

            async with websockets.connect(
                WS_URL,
                ping_interval=20,
                ping_timeout=20
            ) as ws:

                log("✅ CONNECTED")

                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))
                log("📡 Subscription sent.")

                while True:
                    message = await ws.recv()
                    log("📩", message)

                    await send(f"📩 {message}")

        except Exception as e:
            log("❌ Connection Error:", e)
            await send(f"❌ Connection Error:\n{e}")

        log("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)


# =====================================
# Start Program
# =====================================

if __name__ == "__main__":
    asyncio.run(connect())
