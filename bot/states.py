from aiogram.fsm.state import State, StatesGroup


class OrderFlow(StatesGroup):
    waiting_service = State()
    waiting_name = State()
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_birth_place = State()
    waiting_payment = State()
