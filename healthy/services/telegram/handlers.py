from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from aiogram_dialog import (
    Dialog, setup_dialogs, StartMode, Window, DialogManager
)
from aiogram_dialog.widgets.kbd import Button, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from core.models.dataclass_models import *
from core.gateways.gateways import *
from config_reader import load_config
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime

class DialogSG(StatesGroup):
    MAIN = State()
    ADD_NAME = State()
    CONFIRM_TIMEZONE = State()

class DialogSetup:
    def __init__(self):
        self.dialog = self._create_main_dialog()
        self.router = Router()
        self.router.include_router(self.dialog)

    def _create_main_dialog(self) -> Dialog:
        return Dialog(
            Window(
                Format("Привет {user_full_name}!"),
                Const("Давай создадим твой профиль:"),
                Button(
                    Const("Добавить пользователя"),
                    id="add_user",
                    on_click=self.on_add_user
                ),
                state=DialogSG.MAIN,
                getter=self.user_data_getter
            ),
            Window(
                Format("Напиши, как мне тебя лучше звать"),
                TextInput(
                    id="user_name_input",
                    on_success=self.on_name_entered,
                ),
                state=DialogSG.ADD_NAME
            ),
            Window(
                Format("🌍 Твой часовой пояс:"),
                Button(
                    Const("+1"),
                    id="tz_plus_1",
                    on_click=partial(self.on_confirm_timezone, offset=1)
                ),
                Cancel(Const("❌ Отмена")),
                state=DialogSG.CONFIRM_TIMEZONE
            )
        )

    async def user_data_getter(self, dialog_manager: DialogManager, **kwargs):
        return {"user_full_name": dialog_manager.event.from_user.full_name}

    async def on_add_user(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.ADD_NAME)

    async def on_name_entered(self, message: Message, widget: TextInput, dialog_manager: DialogManager, name: str):
        dialog_manager.dialog_data["user_name"] = name
        await dialog_manager.switch_to(DialogSG.CONFIRM_TIMEZONE)

    async def on_confirm_timezone(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager, offset: int):
        user_gateway = dialog_manager.middleware_data["user_gateway"]
        await user_gateway.create_user(
            tg_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=dialog_manager.dialog_data["user_name"],
            timezone=offset
        )
        await dialog_manager.done()
