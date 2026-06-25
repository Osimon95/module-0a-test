import asyncio
from telegram import Bot

TOKEN = HTTP API:8684817654:AAHBznxya0yR7pTRtyjZXIFmGDX9DfWb8K
CHAT_ID = "YOUR_CHAT_ID"

async def main():
    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Module 0A Server Started"
    )

asyncio.run(main())
