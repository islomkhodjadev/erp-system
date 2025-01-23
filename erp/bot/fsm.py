from aiogram.fsm.state import State, StatesGroup

class Login(StatesGroup):
    username = State()
    password = State()



class Support(StatesGroup):
    message = State()