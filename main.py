import os
import asyncio
import logging
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from motor.motor_asyncio import AsyncIOMotorClient
from app.commands import setup_commands


load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGODB_URI = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"

dp = Dispatcher()
client = AsyncIOMotorClient(MONGODB_URI)
db = client['sampleDB']
collection = db['sample_collection']

async def main() -> None:
    """
    Главная функция, запускающая бота.
    Создает объект бота, регистрирует обработчики команд и запускает опрос Telegram API.
    """
    bot = Bot(token=TOKEN)
    setup_commands(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    """
    Точка входа в приложение.
    Настраивает логирование и запускает главную функцию main().
    """
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

