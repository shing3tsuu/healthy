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
                Group(
                    Button(Const("+0"), id="tz_plus_0", on_click=partial(self.handlers.on_confirm_timezone, offset=0)),
                    Button(Const("+1"), id="tz_plus_1", on_click=partial(self.handlers.on_confirm_timezone, offset=1)),
                    Button(Const("+2"), id="tz_plus_2", on_click=partial(self.handlers.on_confirm_timezone, offset=2)),
                    Button(Const("+3"), id="tz_plus_3", on_click=partial(self.handlers.on_confirm_timezone, offset=3)),
                    Button(Const("+4"), id="tz_plus_4", on_click=partial(self.handlers.on_confirm_timezone, offset=4)),
                    Button(Const("+5"), id="tz_plus_5", on_click=partial(self.handlers.on_confirm_timezone, offset=5)),
                    Button(Const("+6"), id="tz_plus_6", on_click=partial(self.handlers.on_confirm_timezone, offset=6)),
                    Button(Const("+7"), id="tz_plus_7", on_click=partial(self.handlers.on_confirm_timezone, offset=7)),
                    Button(Const("+8"), id="tz_plus_8", on_click=partial(self.handlers.on_confirm_timezone, offset=8)),
                    width=3,
                ),
                Cancel(Const("❌ Отмена")),
                state=DialogSG.CONFIRM_TIMEZONE
            ),
            # Window(
            #     Format("Главное меню, здесь ты можешь настраивать свои привычки, читать подсказки и устанавливать напоминания"),
            #  )
        )
