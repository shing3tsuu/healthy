from aiogram.fsm.state import StatesGroup, State

class DialogSG(StatesGroup):
    """ADMIN"""
    ADMIN = State()
    ADMIN_HABIT_MANAGE = State()
    ADMIN_ADD_HABIT = State()

    ADMIN_EDIT_HABIT = State()
    ADMIN_EDIT_HABIT_NAME = State()
    ADMIN_EDIT_HABIT_COST = State()

    ADMIN_ADD_INFO = State()
    ADMIN_ADD_HINT = State()
    ADMIN_ADD_HABIT_COST = State()

    """INTRO"""
    INTRO = State()
    ADD_NAME = State()
    CONFIRM_TIMEZONE = State()

    """MAIN MENU"""
    MAIN_MENU = State()
    USER_HABITS = State()
    ADD_HABIT = State()
    HABIT_DETAIL = State()
    HABIT_STATS = State()
    RELAPSE_TRACKING = State()
