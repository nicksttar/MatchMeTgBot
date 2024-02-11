from aiogram.fsm.state import StatesGroup, State


class Main_Form(StatesGroup):
    lang = State()
    update_lang = State()
    age = State()
    your_gender = State()
    opponent_gende = State()
    city = State()
    name = State()
    about_info = State()
    photo = State()
    result = State()
    buttons = State()
    description = State()