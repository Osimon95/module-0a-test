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
            async with websockets.connect(
                uri,
                additional_headers={"User-Agent": "Python"},
                ping_interval=None  # We will handle pings ourselves
            ) as ws:

                print("✅ CONNECTED")

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="✅ CONNECTED to WEEX WebSocket"
                )

                # Subscribe to a market channel immediately
                await ws.send("""
                {
                    "op":"subscribe",
                    "args":["ticker.BTCUSDT"]
                }
                """)

                while True:
                    # Send heartbeat
                    await ws.ping()

                    # Receive server messages
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=15)
                        print(message)
                    except asyncio.TimeoutError:
                        pass

                    await asyncio.sleep(10)

        except Exception as e:
            print(f"❌ ERROR: {e}")

            try:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"❌ WEEX Connection Error:\n{e}"
                )
            except Exception:
                pass

            print("🔄 Reconnecting in 5 seconds...")
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
    

            
 
