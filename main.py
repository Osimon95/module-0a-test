Telegram Settings
=====================================
TOKEN = "8684817654:AAG48fn13BtVazkR9dCIneC_dItUFUxrXAU"
 CHAT_ID = "8587384068"
bot = Bot(token=TOKEN)
=====================================
Telegram Startup Test
=====================================
async def startup():
 try:
 await bot.send_message(
 chat_id=CHAT_ID,
 text="✅ Bot started on Render"
 )
 print("✅ Telegram startup message sent successfully.")
 except Exception as e:
 print(f"❌ Telegram error: {e}")
=====================================
Main

=====================================
async def main():
 print("🚀 Starting Telegram test...")
 await startup()
 print("🏁 Test completed.")
if name == "main":
 asyncio.run(main())
 

