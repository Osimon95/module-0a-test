import asyncio
import websockets
from telegram import Bot

# =====================================
# Telegram Settings
# =====================================

TOKEN = "8684817654:AAGt2sBu2INI1RPVS5trGnf4jkIW2N7TnDY"
CHAT_ID = "8587384068"

bot = Bot(token=TOKEN)

# =====================================
# Telegram Startup Message
# =====================================

async def startup():
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text="✅ Bot started on Render"
        )
        print("✅ Telegram startup message sent successfully.")
    except Exception as e:
        print(f"❌ Telegram startup error: {e}")

# =====================================
# WEEX Connection
# =====================================

async def connect_weex():
    uri = "wss://ws-contract.weex.com/v3/ws/public"

    try:
        async with websockets.connect(
            uri,
            additional_headers={
                "User-Agent": "Python"
            }
        ) as ws:

            print("✅ CONNECTED to WEEX WebSocket")

            await bot.send_message(
                chat_id=CHAT_ID,
                text="✅ CONNECTED to WEEX WebSocket"
            )

            # Keep connection alive
            while True:
                await asyncio.sleep(60)

    except Exception as e:
        print(f"❌ WEEX ERROR: {e}")

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
    print("🚀 Starting Render service...")
    await startup()
    await connect_weex()

# =====================================
# Entry Point
# =====================================

if __name__ == "__main__":
    asyncio.run(main())
