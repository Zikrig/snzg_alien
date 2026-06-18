from aiogram.fsm.state import State, StatesGroup


class PromoVerifyStates(StatesGroup):
    waiting_phrase = State()
