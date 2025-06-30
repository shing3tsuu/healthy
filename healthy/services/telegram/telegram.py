from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import Dialog, setup_dialogs, DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Awaitable, Dict, Any, Optional
import logging

from core.database.session_manager import create_database_manager, DatabaseManagerBase, DatabaseManagerSQLite
from core.gateways.usergateways import UserGateway

from .states import DialogSG
from .setup import DialogSetup
from .handlers import DialogHandlers
from .getters import DialogGetters

logger = logging.getLogger(__name__)


class IsAdminFilter(BaseFilter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids or []

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in self.admin_ids


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, db_manager: DatabaseManagerBase):
        self.db_manager = db_manager

    async def __call__(self, handler, event, data):
        async with self.db_manager.session() as session:
            data["session"] = session
            data["user_gateway"] = UserGateway(session)
            result = await handler(event, data)
            return result


class TelegramApp:
    def __init__(self, config):
        self.config = config
        self.db_manager = None  # Инициализация отложена
        self.main_router = Router()
        self.bot = None
        self.dp = None
        self.dialog_handlers = DialogHandlers()
        self.dialog_getters = DialogGetters()
        self.dialog_setup = DialogSetup(
            self.dialog_handlers,
            self.dialog_getters
        )

    async def setup(self):
        try:
            # Инициализируем менеджер БД
            self.db_manager = await create_database_manager(self.config)
        except Exception as e:
            logger.critical(f"Database initialization failed: {e}")

            # Аварийный fallback на in-memory SQLite
            logger.info("Using in-memory SQLite as fallback")
            self.config.db.path = ":memory:"
            self.db_manager = DatabaseManagerSQLite(self.config)
            await self.db_manager.initialize()

        self.bot = await self.create_bot()
        self.dp = await self.create_dispatcher()
        self.register_handlers()

    async def run(self):
        await self.db_manager.create_tables()
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    async def create_bot(self) -> Bot:
        return Bot(
            token=self.config.tg_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

    async def create_dispatcher(self) -> Dispatcher:
        dp = Dispatcher(storage=MemoryStorage())

        # Передаем уже инициализированный db_manager
        dp.update.middleware(DatabaseMiddleware(self.db_manager))

        self.main_router.include_router(self.dialog_setup.router)
        dp.include_router(self.main_router)
        setup_dialogs(dp)
        return dp

    def register_handlers(self):
        @self.main_router.message(Command("start"))
        async def start_handler(message: Message, dialog_manager: DialogManager):
            await dialog_manager.start(DialogSG.INTRO)

        @self.main_router.message(Command("admin"))
        async def admin_handler(message: Message, dialog_manager: DialogManager):
            if message.from_user.id not in self.config.tg_bot.admin_ids:
                await self.dialog_handlers.on_admin_access_denied(message)
                return

            await dialog_manager.start(DialogSG.ADMIN)
