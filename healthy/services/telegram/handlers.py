from functools import partial
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window, Dialog
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.input import TextInput

from .states import DialogSG
from core.gateways.gateways import UserGateway

class DialogHandlers:
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