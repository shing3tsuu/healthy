import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict, AsyncGenerator

from aiogram import Bot, Dispatcher, types, BaseMiddleware, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from database import *

from config_reader import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, config):
        self.engine = create_async_engine(
            url=f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.name}",
            pool_size=5,
            max_overflow=5,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                logger.error("Database error: %s", e, exc_info=True)
                await session.rollback()
                raise
            finally:
                await session.close()


class BotMiddleware(BaseMiddleware):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with self.db_manager.session() as session:
            data["session"] = session
            return await handler(event, data)


class Application:
    def __init__(self, config):
        self.config = config
        self.db_manager = DatabaseManager(config)
        self.bot = Bot(
            token=config.tg_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dp = Dispatcher()
        self.router = Router()

    async def setup(self):
        self.dp.update.middleware(BotMiddleware(self.db_manager))
        self.dp.include_router(self.router)

    async def run(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)


async def main():
    config = load_config(".env")
    app = Application(config)
    await app.setup()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())