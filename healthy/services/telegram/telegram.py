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

class IsAdminFilter(BaseFilter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids or []

    async def __call__(self, message: Message | CallbackQuery) -> bool:
        return message.from_user.id in self.admin_ids

class DatabaseMiddleware(BaseMiddleware):
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
            data["user_gateway"] = UserGateway(session)
            data["habit_gateway"] = HabitGateway(session)
            return await handler(event, data)

class DialogManager:
    def __init__(self, user_gateway: UserGateway, habit_gateway: HabitGateway):
        self.user_gateway = user_gateway
        self.habit_gateway = habit_gateway
        self.dialog = Dialog(
            main_window,
            get_user_info_window,
            user_created_window
        )

class TelegramApp:
    def __init__(self, config):
        self.config = config
        self._init_components()

    def _init_components(self):
        self.db_manager = DatabaseManager(self.config)
        self.router = router
        self.bot = self._create_bot()
        self.dp = self._create_dispatcher()
        self._init_dialogs()

    def _create_bot(self) -> Bot:
        try:
            return Bot(
                token=self.config.tg_bot.token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        except Exception as e:
            logger.critical(f"Bot initialization failed: {e}")
            raise

    def _create_dispatcher(self) -> Dispatcher:
        dp = Dispatcher(storage=MemoryStorage())
        dp.update.middleware(DatabaseMiddleware(self.db_manager))
        self._setup_filters(dp)
        dp.include_router(self.router)
        return dp

    def _setup_filters(self, dp: Dispatcher):
        admin_filter = IsAdminFilter(self.config.tg_bot.admin_ids)
        dp.message.filter(admin_filter)
        dp.callback_query.filter(admin_filter)

    def _init_dialogs(self):
        dialog_manager = DialogManager(
            UserGateway(self.db_manager),
            HabitGateway(self.db_manager)
        )
        self.dp.include_router(dialog_manager.dialog)
        setup_dialogs(self.dp)

    async def run(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)