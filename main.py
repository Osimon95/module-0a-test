import asyncio
import websockets
from telegram import Bot

TOKEN = "8684817654:AAEVawL3CPotxilgkxapCcXMs18mV8GdFK"
CHAT_ID = "8587384068"

# Replace with the correct WEEX WebSocket endpoint
WEEX_WS = "wss://wbs-api.weex.com/ws"

bot = Bot(token=TOKEN)

async def connect_weex():
    while True:
        try:
            print("Connecting to WEEX...")

            async with websockets.connect(WEEX_WS) as ws:
                print("CONNECTED")

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="✅ WEEX CONNECTED"
                )

                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=30)
                        print(message)

                    except asyncio.TimeoutError:
                        # Keep the connection alive
                        await ws.ping()

        except Exception as e:
            print(f"Connection failed: {e}")

            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"❌ WEEX Disconnected\n{e}"
            )

            await asyncio.sleep(5)

async def main():

    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Module 0C Worker Started"
    )

    await connect_weex()

if __name__ == "__main__":
    asyncio.run(main())
