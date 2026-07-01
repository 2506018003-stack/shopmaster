from aiogram.fsm.state import State, StatesGroup

class CheckoutState(StatesGroup):
    promo = State()
    address = State()
    phone = State()
    confirm = State()
