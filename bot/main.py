import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

import bot.config as config  # noqa: E402 — load_dotenv must run first
from bot.db import create_tables
from bot.handlers import order, start

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    create_tables()

    proxy_url = os.environ.get("PROXY_URL")
    session = AiohttpSession(proxy=proxy_url) if proxy_url else None
    bot = Bot(token=config.BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(order.router)

    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
