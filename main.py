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
        if len(text) > 3900:
            text = text[:3900] + "\n...(truncated)"

        await bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )

    except Exception as e:
        log("Telegram Error:", e)


# =====================================
# Main Connection
# =====================================

async def connect():

    while True:

        try:

            log("Connecting to WEEX...")

            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "Python"
                },
                ping_interval=20,
                ping_timeout=20,
                max_size=None
            ) as ws:

                log("CONNECTED")

                await send("✅ CONNECTED to WEEX WebSocket")

                # Subscribe
                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))

                log("Subscription sent:")
                log(json.dumps(SUBSCRIBE_MESSAGE))

                await send("📡 Subscription sent.")

                while True:

                    message = await ws.recv()

                    log("=" * 60)
                    log("RAW MESSAGE")
                    log(message)
                    log("=" * 60)

                    await send(f"📩 {message}")

                    try:
                        data = json.loads(message)

                    except Exception:
                        continue

                    if not isinstance(data, dict):
                        continue

                    # --------------------------------
                    # Heartbeat: {"event":"ping","time":"..."}
                    # --------------------------------
                    if data.get("event") == "ping":

                        pong = {
                            "event": "pong",
                            "time": data.get("time")
                        }

                        await ws.send(json.dumps(pong))
                        log("Sent:", pong)

                    # --------------------------------
                    # Heartbeat: {"ping":123456}
                    # --------------------------------
                    elif "ping" in data:

                        pong = {
                            "pong": data["ping"]
                        }

                        await ws.send(json.dumps(pong))
                        log("Sent:", pong)

                    # --------------------------------
                    # Heartbeat: {"op":"ping"}
                    # --------------------------------
                    elif data.get("op") == "ping":

                        pong = {
                            "op": "pong"
                        }

                        await ws.send(json.dumps(pong))
                        log("Sent:", pong)

        except websockets.ConnectionClosed as e:

            log(f"Connection closed: {e}")

            await send(f"❌ Connection closed:\n{e}")

        except Exception as e:

            log("Connection Error:", e)

            await send(f"❌ Connection Error:\n{e}")

        log("Reconnecting in 5 seconds...")

        await asyncio.sleep(5)


# =====================================
# Start
# =====================================

if __name__ == "__main__":
    asyncio.run(connect())
