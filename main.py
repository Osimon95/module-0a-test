import asyncio
import json
import websockets

# =====================================
# WEEX WebSocket Settings
# =====================================

WS_URL = "wss://ws-contract.weex.com/v3/ws/public"


async def main():
    while True:
        try:
            async with websockets.connect(
                WS_URL,
                additional_headers={
                    "User-Agent": "WEEX-BTC-Bot/1.0"
                },
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10
            ) as ws:

                print("CONNECTED")

                # Correct WEEX V3 ticker subscription
                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        "BTCUSDT@ticker"
                    ],
                    "id": 1
                }

                await ws.send(json.dumps(subscribe_message))

                while True:
                    message = await ws.recv()

                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        continue

                    # WEEX application-level ping
                    if data.get("event") == "ping":
                        pong_message = {
                            "method": "PONG",
                            "id": 1
                        }

                        await ws.send(json.dumps(pong_message))
                        continue

                    # Subscription acknowledgement
                    if "result" in data:
                        if data.get("result") is True:
                            print("SUBSCRIBED")
                        else:
                            print(
                                "SUBSCRIPTION ERROR:",
                                data.get("msg", data)
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
                                    print(price)

        except asyncio.CancelledError:
            raise

        except websockets.ConnectionClosed as error:
            print(f"DISCONNECTED: {error}")

        except Exception as error:
            print(f"CONNECTION ERROR: {error}")

        # Reconnect after disconnection
        print("RECONNECTING IN 5 SECONDS...")
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("STOPPED")
imp
