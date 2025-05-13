from aiogram_dialog import DialogManager

class DialogGetters:
    @staticmethod
    async def user_data_getter(dialog_manager: DialogManager, **kwargs):
        user = dialog_manager.event.from_user
        return {
            "user_full_name": user.full_name if user else "Гость"
        }