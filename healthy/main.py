import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict, AsyncGenerator
import winloop

import sqlalchemy as db
from aiogram import Bot, Dispatcher, types, BaseMiddleware, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from core.database.database import *
from services.telegram.handlers import *
from services.telegram.telegram import *
from config_reader import load_config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    try:
        config = load_config(".env")
        tg_app = TelegramApp(config)
        await tg_app.run()
    except Exception as e:
        logger.exception("Application failed to start: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    winloop.install()
    asyncio.run(main())
