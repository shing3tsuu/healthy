from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Dict, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import sqlalchemy as db
import logging

from .structures import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, config):
        self.engine = create_async_engine(
            url=f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.name}",
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
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

    async def create_tables(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)