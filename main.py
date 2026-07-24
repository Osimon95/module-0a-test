import asyncio
import json
import websockets

# =====================================
# WEEX WebSocket Settings
# =====================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"


async def main():
    try:
        async with websockets.connect(
            WS_URL,
            ping_interval=20,
            ping_timeout=20
        ) as ws:

            print("CONNECTED")

            # Subscribe to BTCUSDT ticker
            subscribe = {
                "op": "subscribe",
                "args": [
                    "ticker.BTCUSDT"
                ]
            }

            await ws.send(json.dumps(subscribe))

            while True:
                try:
                    message = await ws.recv()

                    # Parse JSON
                    try:
                        data = json.loads(message)
                    except:
                        continue

                    # Ignore ping/pong and subscription acknowledgements
                    if "ping" in data or "pong" in data:
                        continue

                    # Look for ticker data
                    if "data" in data:
                        ticker = data["data"]

                        if isinstance(ticker, dict):
                            price = (
                                ticker.get("lastPrice")
                                or ticker.get("last")
                                or ticker.get("price")
                                or ticker.get("close")
                            )

                            if price is not None:
                                print(price)

                except websockets.ConnectionClosed:
                    print("DISCONNECTED")
                    break

    except Exception as e:
        print(f"Connection Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
