import asyncio
import websockets
from telegram import Bot

TOKEN = "8684817654:AAG48fn13BtVazkR9dCIneC_dItUFUxrXAU"
CHAT_ID = "8587384068"

async def test():
    bot = Bot(token=TOKEN)
    uri = "wss://ws-contract.weex.com/v3/ws/public"

    try:
        async with websockets.connect(
            uri,
            additional_headers={"User-Agent": "Python"}
        ) as ws:
            print("CONNECTED")

            await bot.send_message(
                chat_id=CHAT_ID,
                text="✅ CONNECTED to WEEX WebSocket"
            )

            # Keep the connection alive
            while True:
                await asyncio.sleep(60)

    except Exception as e:
        print(f"ERROR: {e}")

        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"❌ WEEX Connection Error:\n{e}"
            )
        except Exception:
            pass

asyncio.run(test())
