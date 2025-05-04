from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window
)
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from core.models.dataclass_models import *
from core.gateways.gateways import *
from config_reader import load_config
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

class MySG(StatesGroup):
    main = State()
    get_user_info = State()
    user_created = State()

router = Router()


get_user_info_window = Window(
    Format("Please enter your name:"),
    TextInput(id="name"),
    state=MySG.get_user_info,
)

main_window = Window(
    Const("Hello, unknown person"),
    Button(Const("Create User"), id="create_user"),
    Cancel(),
    state=MySG.main,
)

user_created_window = Window(
    Format("User {name} successfully created!"),
    state=MySG.user_created,
)

dialog = Dialog(
    main_window,
    get_user_info_window,
    user_created_window
)

@router.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


# Обработчик события нажатия кнопки "Create User"
async def create_user(callback_query: CallbackQuery, dialog_manager: DialogManager, user_gateway: UserGateway):
    await dialog_manager.switch_to(MySG.get_user_info)


async def process_name(message: Message, dialog_manager: DialogManager, user_gateway: UserGateway):
    user_name = dialog_manager.dialog_data.get("name")
    try:
        user = await user_gateway.create_user(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            first_name=user_name,
            timezone="UTC",
        )
        await dialog_manager.switch_to(MySG.user_created)
    except Exception as e:
        await dialog_manager.show(Window(Const(f"Error creating user: {e}")))