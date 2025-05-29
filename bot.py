import os
from aiogram import Bot, Dispatcher, executor, types
from handlers import register_handlers
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
