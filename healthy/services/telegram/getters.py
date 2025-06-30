from aiogram_dialog import DialogManager

class DialogGetters:
    @staticmethod
    async def admin_habits_getter(dialog_manager: DialogManager, **kwargs):
        habits = dialog_manager.dialog_data.get("admin_habits", [])
        return {
            "habits": habits,
            "habits_count": len(habits)
        }

    @staticmethod
    async def current_habit_getter(dialog_manager: DialogManager, **kwargs):
        habit = dialog_manager.dialog_data.get("current_habit")
        return {
            "habit_name": habit.name if habit else "Не выбрано",
            "habit_cost": habit.cost_per_unit if habit else 0,
            "info_count": len(habit.info) if habit else 0,
            "hints_count": len(habit.hints) if habit else 0
        }

    @staticmethod
    async def user_data_getter(dialog_manager: DialogManager, **kwargs):
        user = dialog_manager.event.from_user
        return {
            "user_full_name": user.full_name if user else "Гость"
        }

    @staticmethod
    async def user_habits_getter(dialog_manager: DialogManager, **kwargs):
        user_gateway = dialog_manager.middleware_data["user_gateway"]
        user = await user_gateway.get_user_by_tg_id(dialog_manager.event.from_user.id)
        habits = await user_gateway.get_user_habit_by_id(user.id)

        return {
            "habits": habits,
            "habits_count": len(habits),
            "total_saved": sum(h.saved_money for h in habits)
        }

    @staticmethod
    async def habit_detail_getter(dialog_manager: DialogManager, **kwargs):
        habit_id = dialog_manager.dialog_data.get("habit_id")
        session = dialog_manager.middleware_data["session"]
        user_gateway = UserGateway(session)

        # Заглушка для демонстрации
        return {
            "habit_name": "Курение",
            "streak_days": 15,
            "saved_money": 3750,
            "last_relapse": (datetime.now() - timedelta(days=5)).strftime("%d.%m.%Y"),
            "cost_per_day": 250
        }

    @staticmethod
    async def all_habits_getter(dialog_manager: DialogManager, **kwargs):
        # В реальном приложении - запрос к БД
        return {
            "habits": [
                {"id": 1, "name": "Курение", "cost": 250},
                {"id": 2, "name": "Фастфуд", "cost": 350},
                {"id": 3, "name": "Алкоголь", "cost": 500},
            ]
        }
