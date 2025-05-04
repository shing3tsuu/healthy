from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import Dialog, setup_dialogs
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Awaitable, Dict, Any
import logging

from core.database.manager import DatabaseManager
from core.gateways.gateways import HabitGateway, UserGateway
from services.telegram.handlers import *

logger = logging.getLogger(__name__)


class DialogSG(StatesGroup):
    MAIN = State()


class IsAdminFilter(BaseFilter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids or []

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in self.admin_ids


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def __call__(self, handler, event, data):
        async with self.db_manager.session() as session:
            data["session"] = session
            data["user_gateway"] = UserGateway(session)
            data["habit_gateway"] = HabitGateway(session)
            return await handler(event, data)


class DialogManager:
    def __init__(self):
        self.dialog = self._create_main_dialog()
        self.router = Router()
        self.router.include_router(self.dialog)

    def _create_main_dialog(self) -> Dialog:
        return Dialog(
            Window(
                Const("Добро пожаловать!"),
                state=DialogSG.MAIN
            )
        )

class TelegramApp:
    def __init__(self, config):
        self.config = config
        self.db_manager = DatabaseManager(config)
        self.main_router = Router()
        self.bot = None
        self.dp = None

    async def create_bot(self) -> Bot:
        return Bot(
            token=self.config.tg_bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

    async def create_dispatcher(self) -> Dispatcher:
        dp = Dispatcher(storage=MemoryStorage())
        dp.update.middleware(DatabaseMiddleware(self.db_manager))

        dialog_manager = DialogManager()
        self.main_router.include_router(dialog_manager.router)

        dp.include_router(self.main_router)
        setup_dialogs(dp)
        return dp

    async def setup(self):
        self.bot = await self.create_bot()
        self.dp = await self.create_dispatcher()
        self.register_handlers()

    def register_handlers(self):
        @self.main_router.message(Command("start"))
        async def start_handler(message: Message, dialog_manager: DialogManager):
            await dialog_manager.start(DialogSG.MAIN)

    async def run(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)
