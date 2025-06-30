from cgitb import handler
from datetime import timezone

from aiogram import Router
from aiogram_dialog import (
    Dialog, setup_dialogs, StartMode, Window, DialogManager
)
from aiogram_dialog.widgets.kbd import (
    Button, Back, Cancel, Group, ListGroup, Select, SwitchTo, Row, ScrollingGroup
)
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from functools import partial
import pytz

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

    def create_timezone_buttons(self) -> Group:
        buttons = []
        timezones = {
            "Europe/Moscow": "UTC+3",
            "Europe/Samara": "UTC+4",
            "Asia/Yekaterinburg": "UTC+5",
            "Asia/Omsk": "UTC+6",
            "Asia/Krasnoyarsk": "UTC+7",
            "Asia/Irkutsk": "UTC+8",
            "Asia/Yakutsk": "UTC+9",
            "Asia/Vladivostok": "UTC+10",
            "Asia/Magadan": "UTC+11",
            "Asia/Kamchatka": "UTC+12"
        }
        id: int = 0

        for timezone, utc in timezones.items():
            buttons.append(
                Button(
                    Const(f"{timezone} ({utc})"),
                    id=f"tz_{id}",
                    on_click=partial(self.handlers.on_confirm_timezone, timezone=timezone),
                )
            )
            id += 1
        return Group(*buttons, width=1)

    def _create_dialog(self) -> Dialog:
        return Dialog(

            # Админ-панель
            Window(
                Const("⚙️ Админ-панель"),
                Const("\nВыберите действие:"),
                Button(
                    Const("📋 Управление привычками"),
                    id="manage_habits",
                    on_click=self.handlers.on_show_all_habits,
                ),
                Button(
                    Const("➕ Добавить новую привычку"),
                    id="add_new_habit",
                    on_click=self.handlers.on_add_new_habit,
                ),
                state=DialogSG.ADMIN
            ),

            # Управление привычками (список)
            Window(
                Format("📋 Все привычки ({habits_count}):"),

                ListGroup(
                    Select(
                        text=Format("📌 {item.name}"),
                        id="habits_select_admin",
                        item_id_getter=lambda item: str(item.id),
                        items="habits",
                        on_click=self.handlers.on_habit_selected_admin,
                    ),
                    item_id_getter=lambda item: str(item.id),
                    items="habits",
                    id="admin_habits_group"
                ),

                SwitchTo(
                    Const("⬅️ Назад"),
                    id="back_admin",
                    state=DialogSG.ADMIN
                ),
                state=DialogSG.ADMIN_HABIT_MANAGE,
                getter=self.getters.admin_habits_getter
            ),

            # Редактирование конкретной привычки
            Window(
                Format("📌 Редактирование: {habit_name}"),
                Format("\n💵 Стоимость: {habit_cost} ₽/день"),
                Format("ℹ️ Информационных блоков: {info_count}"),
                Format("💡 Подсказок: {hints_count}"),

                Row(
                    Button(
                        Const("✏️ Изменить название"),
                        id="edit_name",
                        on_click=partial(self.handlers.on_start_input, state=DialogSG.ADMIN_EDIT_HABIT_NAME),
                    ),
                    Button(
                        Const("💰 Изменить стоимость"),
                        id="edit_cost",
                        on_click=partial(self.handlers.on_start_input, state=DialogSG.ADMIN_EDIT_HABIT_COST),
                    ),
                ),
                Row(
                    Button(
                        Const("ℹ️ Добавить информацию"),
                        id="add_info",
                        on_click=self.handlers.on_add_info,
                    ),
                    Button(
                        Const("💡 Добавить подсказку"),
                        id="add_hint",
                        on_click=partial(self.handlers.on_add_info, type_="hint"),
                    ),
                ),
                SwitchTo(
                    Const("⬅️ Назад"),
                    id="back_habits_list",
                    state=DialogSG.ADMIN_HABIT_MANAGE
                ),
                state=DialogSG.ADMIN_EDIT_HABIT,
                getter=self.getters.current_habit_getter
            ),

            # Добавление новой привычки
            Window(
                Const("➕ Создание новой привычки"),
                Const("\nВведите название привычки:"),
                TextInput(
                    id="habit_name_input",
                    on_success=self.handlers.on_habit_name_entered,
                ),
                SwitchTo(
                    Const("❌ Отмена"),
                    id="cancel_add",
                    state=DialogSG.ADMIN
                ),
                state=DialogSG.ADMIN_ADD_HABIT
            ),

            Window(
                Const("💰 Введите стоимость за день (число):"),
                Const("\nИли отправьте 0, если стоимость не учитывается"),
                TextInput(
                    id="habit_cost_input",
                    type_factory=float,
                    on_success=self.handlers.on_habit_cost_entered,
                ),
                state=DialogSG.ADMIN_ADD_HABIT_COST
            ),

            # Добавление информации
            Window(
                Const("ℹ️ Добавление информационного блока"),
                Const("\nВведите текст информации:"),
                TextInput(
                    id="info_text_input",
                    on_success=self.handlers.on_info_entered,
                ),
                SwitchTo(
                    Const("❌ Отмена"),
                    id="cancel_info",
                    state=DialogSG.ADMIN_EDIT_HABIT
                ),
                state=DialogSG.ADMIN_ADD_INFO
            ),

# ------------------------

            # Регистрация
            Window(
                Format("Привет {user_full_name}!"),
                Const("Давай создадим твой профиль:"),
                Button(
                    Const("Добавить пользователя"),
                    id="add_user",
                    on_click=self.handlers.on_add_user
                ),
                state=DialogSG.INTRO,
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
                self.create_timezone_buttons(),
                state=DialogSG.CONFIRM_TIMEZONE
            ),

# ------------------------

            # Главное меню
            Window(
                Format("👋 Привет, {user_full_name}!"),
                Const("\n🛠️ Выберите действие:"),
                Button(
                    Const("📋 Мои привычки"),
                    id="user_habits",
                    on_click=self.handlers.on_user_habits,
                ),
                Button(
                    Const("➕ Добавить привычку"),
                    id="add_habit",
                    on_click=self.handlers.on_add_habit,
                ),
                Button(
                    Const("📊 Общая статистика"),
                    id="show_stats",
                    on_click=self.handlers.on_show_stats,
                ),
                state=DialogSG.MAIN_MENU,
                getter=self.getters.user_data_getter
            ),

            # Список привычек пользователя
            Window(
                Format("📋 Ваши привычки:"),
                Format("\nВсего привычек: {habits_count}"),
                Format("Суммарно сэкономлено: {total_saved} ₽"),

                ListGroup(
                    Select(
                        text=Format("📌 {item.name}"),
                        id="habits_select",
                        item_id_getter=lambda item: item.id,
                        items="habits",
                        on_click=self.handlers.on_habit_selected,
                    ),
                    item_id_getter=lambda item: item.id,
                    items="habits",
                    id="habits_group",
                ),

                SwitchTo(
                    Const("⬅️ Назад"),
                    id="back_main",
                    state=DialogSG.MAIN_MENU
                ),
                state=DialogSG.USER_HABITS,
                getter=self.getters.user_habits_getter
            ),

            # Детали привычки
            Window(
                Format("📌 Привычка: {habit_name}"),
                Format("\n🔥 Текущая серия: {streak_days} дней"),
                Format("💸 Сэкономлено: {saved_money} ₽"),
                Format("⏱ Последний рецидив: {last_relapse}"),
                Format("\n💵 Траты в день: {cost_per_day} ₽"),

                Row(
                    Button(
                        Const("📉 Зафиксировать рецидив"),
                        id="track_relapse",
                        on_click=self.handlers.on_track_relapse,
                    ),
                    Button(
                        Const("📊 Статистика"),
                        id="habit_stats",
                        on_click=self.handlers.on_show_stats,
                    ),
                ),
                SwitchTo(
                    Const("⬅️ Назад"),
                    id="back_habits",
                    state=DialogSG.USER_HABITS
                ),
                state=DialogSG.HABIT_DETAIL,
                getter=self.getters.habit_detail_getter
            ),

            # Добавление новой привычки
            Window(
                Const("➕ Выберите привычку для добавления:"),

                ScrollingGroup(
                    Select(
                        text=Format("{item.name} - {item.cost} ₽/день"),
                        id="all_habits_select",
                        item_id_getter=lambda item: item["id"],
                        items="habits",
                        on_click=self.handlers.on_habit_selected,
                    ),
                    id="all_habits_group",
                    width=1,
                    height=5,
                ),

                SwitchTo(
                    Const("⬅️ Назад"),
                    id="back_main",
                    state=DialogSG.MAIN_MENU
                ),
                state=DialogSG.ADD_HABIT,
                getter=self.getters.all_habits_getter
            ),

            # Статистика привычки
            Window(
                Format("📊 Статистика по привычке: {habit_name}"),
                Const("\n📈 График прогресса..."),
                Format("\n🔥 Самая длинная серия: 30 дней"),
                Format("📉 Всего рецидивов: 5"),
                Format("\n💵 Всего сэкономлено: {saved_money} ₽"),

                SwitchTo(
                    Const("⬅️ Назад"),
                    id="back_detail",
                    state=DialogSG.HABIT_DETAIL
                ),
                state=DialogSG.HABIT_STATS,
                getter=self.getters.habit_detail_getter
            ),

            # Трекинг рецидива
            Window(
                Const("🚨 Подтвердите рецидив"),
                Format("\nПривычка: {habit_name}"),
                Const("\nПричина рецидива:"),
                # Здесь можно добавить TextInput для причины

                Row(
                    Button(
                        Const("✅ Подтвердить"),
                        id="confirm_relapse",
                        on_click=self.handlers.on_confirm_relapse,
                    ),
                    SwitchTo(
                        Const("❌ Отмена"),
                        id="cancel_relapse",
                        state=DialogSG.HABIT_DETAIL
                    ),
                ),
                state=DialogSG.RELAPSE_TRACKING,
                getter=self.getters.habit_detail_getter
            )
        )
