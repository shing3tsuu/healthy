from aiogram.fsm.state import StatesGroup, State

class DialogSG(StatesGroup):
    MAIN = State()
    ADD_NAME = State()
    CONFIRM_TIMEZONE = State()