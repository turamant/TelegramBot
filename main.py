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

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

client = AsyncIOMotorClient(MONGODB_URI)
db = client[f"{os.getenv('MONGO_DB')}"]
collection = db['sample_collection']

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN)

    # Setup commands
    setup_commands(dp)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

