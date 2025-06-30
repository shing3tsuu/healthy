import logging
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import asyncio
import os
import sqlalchemy as db

from .structures import Base

logger = logging.getLogger(__name__)


class DatabaseManagerBase:
    """Базовый класс для менеджеров БД"""
    def __init__(self, config):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.session_factory = None

    async def initialize(self):
        """Асинхронная инициализация движка"""
        raise NotImplementedError()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.engine:
            await self.initialize()

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
        if not self.engine:
            await self.initialize()

        async with self.engine.begin() as conn:
            if isinstance(self.engine.url, str) and "sqlite" in self.engine.url:
                await conn.execute("PRAGMA foreign_keys=ON")
            await conn.run_sync(Base.metadata.create_all)


class DatabaseManager(DatabaseManagerBase):
    """Реализация для PostgreSQL"""
    async def initialize(self):
        from sqlalchemy.ext.asyncio import create_async_engine

        self.engine = create_async_engine(
            url=f"postgresql+asyncpg://{self.config.db.user}:{self.config.db.password}@{self.config.db.host}:{self.config.db.port}/{self.config.db.name}",
            pool_size=5,
            max_overflow=10,
            connect_args={"timeout": 5}  # Таймаут на подключение 5 секунд
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

class DatabaseManagerSQLite(DatabaseManagerBase):
    """Реализация для SQLite"""
    async def initialize(self):
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.pool import NullPool
        db_path = self.config.db.path or "sqlite.db"

        if db_path != ":memory:":
            db_path = os.path.abspath(db_path)
            dir_path = os.path.dirname(db_path)

            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created database directory: {dir_path}")

        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=NullPool
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        logger.debug(f"SQLite database initialized at {db_path}")

async def create_database_manager(config) -> Union[DatabaseManager, DatabaseManagerSQLite]:
    """Создает менеджер БД с автоматическим выбором типа"""
    if all([config.db.host, config.db.port, config.db.name,
            config.db.user, config.db.password]):
        try:
            postgres_db = DatabaseManager(config)
            await postgres_db.initialize()

            # Проверяем соединение
            async with postgres_db.session() as session:
                await session.execute(db.text("SELECT 1"))

            logger.info("Using PostgreSQL database")
            return postgres_db
        except Exception as e:
            logger.critical(f"PostgreSQL connection failed: {e}")

    sqlite_db = DatabaseManagerSQLite(config)
    await sqlite_db.initialize()
    logger.info(f"Using SQLite database at {config.db.path or 'sqlite.db'}")
    return sqlite_db
