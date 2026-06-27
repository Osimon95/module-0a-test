import asyncio
import websockets

async def test():
    uri = "wss://ws-contract.weex.com/v3/ws/public"

    async with websockets.connect(
        uri,
        additional_headers={"User-Agent": "Python"}
    ) as ws:
        print("CONNECTED")

asyncio.run(test())
