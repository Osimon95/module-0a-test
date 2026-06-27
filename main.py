import asyncio
import json
from datetime import datetime

import websockets

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
    print(f"[{now}]", *args, flush=True)


# =====================================
# Main
# =====================================

async def main():
    while True:
        try:
            async with websockets.connect(
                WS_URL,
                ping_interval=20,
                ping_timeout=20,
            ) as ws:

                log("✅ CONNECTED to WEEX WebSocket")

                # Subscribe to BTCUSDT ticker
                await ws.send(json.dumps(SUBSCRIBE_MESSAGE))
                log("📡 Subscription sent:", SUBSCRIBE_MESSAGE)

                # Receive messages
                async for message in ws:
                    try:
                        data = json.loads(message)
                    except Exception:
                        log("📩", message)
                        continue

                    # Ignore ping events
                    if data.get("event") == "ping":
                        continue

                    log("📩", json.dumps(data))

        except Exception as e:
            log("❌ Connection Error:", e)
            log("🔄 Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
