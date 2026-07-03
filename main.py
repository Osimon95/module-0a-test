import asyncio
import websockets
from telegram import Bot

# =====================================
# Telegram Settings
# =====================================

TOKEN = "8684817654:AAGEg4UwrTbeTMzaSyt4idE1TFYnPqFXtjw"
CHAT_ID = "8587384068"

bot = Bot(token=TOKEN)

# =====================================
# Startup Message
# =====================================

async def startup():
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="✅ Bot started on Render"
        )
        print("✅ Telegram startup message sent successfully.")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# =====================================
# WEEX WebSocket Connection
# =====================================

async def connect_weex():
    uri = "wss://ws-contract.weex.com/v3/ws/public"

    while True:
    try:
        print("Connecting to WEEX...")

        async with websockets.connect(
            uri,
            additional_headers={"User-Agent": "Python"},
            ping_interval=None
        ) as ws:

            print("CONNECTED")

            await ws.send(json.dumps({
                "op": "subscribe",
                "args": ["ticker.BTCUSDT"]
            }))

            print("Subscribed")

            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=20)

                    print(msg)

                except asyncio.TimeoutError:
                    print("Sending ping...")
                    await ws.ping()

    except Exception as e:
        print(f"WEEX ERROR: {repr(e)}")

        try:
            await bot.send_message(
                CHAT_ID,
                f"WEEX ERROR:\n{repr(e)}"
            )
        except Exception:
            pass

        print("Reconnect in 5 seconds...")
        await asyncio.sleep(5)
        

# =====================================
# Main
# =====================================

async def main():
    print("🚀 Starting bot...")
    await startup()
    await connect_weex()

if __name__ == "__main__":
    asyncio.run(main())
    

            
 
