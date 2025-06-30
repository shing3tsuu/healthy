from functools import partial
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window, Dialog
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.input import TextInput
from aiogram.fsm.state import State
from typing import Any

from .states import DialogSG
from core.gateways.usergateways import UserGateway

class DialogHandlers:

    """ADMIN_MENU"""

    async def on_start_input(self, callback: CallbackQuery, button: Button,
                             dialog_manager: DialogManager, state: State):
        input_type = state.state.split(":")[-1].lower()
        dialog_manager.dialog_data["input_type"] = input_type
        await dialog_manager.switch_to(state)

    async def on_admin_access_denied(self, message: Message):
        await message.answer("⛔ У вас нет прав доступа к админ-панели")

    async def on_admin_menu(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.ADMIN_HABIT_MANAGE)

    async def on_show_all_habits(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        user_gateway = dialog_manager.middleware_data["user_gateway"]
        habits = await user_gateway.get_all_habits()
        dialog_manager.dialog_data["admin_habits"] = habits
        await dialog_manager.switch_to(DialogSG.ADMIN_EDIT_HABIT)

    async def on_habit_selected_admin(self, callback: CallbackQuery, widget: Any,
                                      dialog_manager: DialogManager, habit_id: str):
        habit_id = int(habit_id)
        dialog_manager.dialog_data["current_habit_id"] = habit_id

        # Получаем привычку для отображения
        user_gateway = dialog_manager.middleware_data["user_gateway"]
        try:
            habit = await user_gateway.get_habit_by_id(habit_id)
            dialog_manager.dialog_data["current_habit"] = habit
        except NotFoundError:
            await callback.answer("Привычка не найдена!")
            return

        await dialog_manager.switch_to(DialogSG.ADMIN_EDIT_HABIT)

    async def on_add_new_habit(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.ADMIN_ADD_HABIT)

    async def on_habit_name_entered(self, message: Message, widget: TextInput,
                                    dialog_manager: DialogManager, name: str):
        dialog_manager.dialog_data["new_habit_name"] = name
        await dialog_manager.switch_to(DialogSG.ADMIN_ADD_HABIT_COST)

    async def on_habit_cost_entered(self, message: Message, widget: TextInput,
                                    dialog_manager: DialogManager, cost: str):
        try:
            cost_value = float(cost) if cost else None
            dialog_manager.dialog_data["new_habit_cost"] = cost_value
        except ValueError:
            await message.answer("⚠️ Введите число или оставьте поле пустым")
            return

        # Создаем привычку
        user_gateway = dialog_manager.middleware_data["user_gateway"]
        new_habit = await user_gateway.create_habit(
            name=dialog_manager.dialog_data["new_habit_name"],
            cost_per_unit=cost_value,
            info=[],
            hints=[]
        )

        await message.answer(f"✅ Привычка '{new_habit.name}' создана!")
        await dialog_manager.switch_to(DialogSG.ADMIN_HABIT_MANAGE)

    async def on_add_info(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.ADMIN_ADD_INFO)

    async def on_info_entered(self, message: Message, widget: TextInput,
                              dialog_manager: DialogManager, text: str):
        # Сохраняем информацию для текущей привычки
        habit_id = dialog_manager.dialog_data["current_habit_id"]
        user_gateway = dialog_manager.middleware_data["user_gateway"]

        # В реальности нужно разделить название и описание
        await user_gateway.add_info_to_habit(
            habit_id=habit_id,
            name="Информация",
            description=text
        )

        await message.answer("✅ Информация добавлена!")
        await dialog_manager.switch_to(DialogSG.ADMIN_EDIT_HABIT)

    """INTRO"""

    async def on_add_user(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.ADD_NAME)

    async def on_name_entered(self, message: Message, widget: TextInput, dialog_manager: DialogManager, name: str):
        dialog_manager.dialog_data["user_name"] = name
        await dialog_manager.switch_to(DialogSG.CONFIRM_TIMEZONE)

    async def on_confirm_timezone(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager, timezone: str):
        user_gateway = dialog_manager.middleware_data["user_gateway"]
        await user_gateway.create_user(
            tg_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=dialog_manager.dialog_data["user_name"],
            timezone=timezone
        )
        await dialog_manager.switch_to(DialogSG.MAIN_MENU)

    """MAIN MENU"""

    async def on_main_menu(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.MAIN_MENU)

    async def on_user_habits(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.USER_HABITS)

    async def on_add_habit(self, callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.ADD_HABIT)

    async def on_habit_selected(self, callback: CallbackQuery, button: Button,
                                dialog_manager: DialogManager, habit_id: int):
        dialog_manager.dialog_data["habit_id"] = habit_id
        await dialog_manager.switch_to(DialogSG.HABIT_DETAIL)

    async def on_show_stats(self, callback: CallbackQuery, button: Button,
                            dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.HABIT_STATS)

    async def on_track_relapse(self, callback: CallbackQuery, button: Button,
                               dialog_manager: DialogManager):
        await dialog_manager.switch_to(DialogSG.RELAPSE_TRACKING)

    async def on_confirm_relapse(self, callback: CallbackQuery, button: Button,
                                 dialog_manager: DialogManager):
        habit_id = dialog_manager.dialog_data["habit_id"]
        session = dialog_manager.middleware_data["session"]
        user_gateway = UserGateway(session)

        # Здесь будет логика трекинга рецидива
        await callback.answer("Рецидив зафиксирован!")
        await dialog_manager.switch_to(DialogSG.HABIT_DETAIL)
