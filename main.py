import asyncio
import websockets
from telegram import Bot

# =====================================
# Telegram Settings
# =====================================

TOKEN = "8684817654:AAELTeEuXGxn9dRUaE_QRJRqAspSTraitjk"
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

# =====================================
# Main
# =====================================

async def main():
    print("🚀 Starting bot...")
    await startup()
    await connect_weex()

if __name__ == "__main__":
    asyncio.run(main())
 
