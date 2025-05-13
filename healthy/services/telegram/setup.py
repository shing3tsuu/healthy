from aiogram import Router
from aiogram_dialog import (
    Dialog, setup_dialogs, StartMode, Window, DialogManager
)
from aiogram_dialog.widgets.kbd import Button, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from functools import partial

from .states import DialogSG
from .getters import DialogGetters
from .handlers import DialogHandlers


class DialogSetup:
    def __init__(self, handlers: DialogHandlers, getters: DialogGetters):
        self.handlers = handlers
        self.getters = getters
        self.router = Router()
        self.dialog = self._create_dialog()
        self.router.include_router(self.dialog)

    def _create_dialog(self) -> Dialog:
        return Dialog(
            Window(
                Format("Привет {user_full_name}!"),
                Const("Давай создадим твой профиль:"),
                Button(
                    Const("Добавить пользователя"),
                    id="add_user",
                    on_click=self.handlers.on_add_user
                ),
                state=DialogSG.MAIN,
                getter=self.getters.user_data_getter
            ),
            Window(
                Format("Напиши, как мне тебя лучше звать"),
                TextInput(
                    id="user_name_input",
                    on_success=self.handlers.on_name_entered,
                ),
                state=DialogSG.ADD_NAME
            ),
            Window(
                Format("🌍 Твой часовой пояс:"),
                Button(
                    Const("+1"),
                    id="tz_plus_1",
                    on_click=partial(self.handlers.on_confirm_timezone, offset=1)
                ),
                Cancel(Const("❌ Отмена")),
                state=DialogSG.CONFIRM_TIMEZONE
            )
        )