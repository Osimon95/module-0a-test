import asyncio
from telegram import Bot

TOKEN = "8684817654:AAG4UhWjKMxqzTRfZPeaKLWqaAAOFa5xt-s"
CHAT_ID = "8587384068"

async def main():
    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Module 0A Server Started"
    )

asyncio.run(main())
