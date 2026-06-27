import asyncio
import json
from datetime import datetime

import websockets

# =====================================
# WEEX Settings
# =====================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"

SUBSCRIBE_MESSAGE = {
    "method": "SUBSCRIBE",
    "params": [
        "BTCUSDT@ticker"
    ],
    "id": 1
}

# =====================================
# Helpers
# =====================================

def log(*args):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}]", *args)

# =====================================
# Main
# =====================================

async def main():
    while True:
        try:
            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "Python-Module-0D"
                },
                ping_interval=None,
                close_timeout=10,
            ) as ws:

                log("✅ CONNECTED to WEEX WebSocket")

                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))
                log("📡 Subscription sent:", SUBSCRIBE_MESSAGE)

                while True:
                    message = await ws.recv()
                    log("📩", message)

                    try:
                        data = json.loads(message)
                    except Exception:
                        continue

                    # Respond to server ping
                    if data.get("event") == "ping":
                        pong = {
                            "method": "PONG",
                            "id": 1
                        }
                        await ws.send(json.dumps(pong))
                        log("🏓 PONG sent")

        except Exception as e:
            log("❌ Connection Error:", e)
            log("🔄 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

# =====================================
# Start
# =====================================

if __name__ == "__main__":
    asyncio.run(main())
