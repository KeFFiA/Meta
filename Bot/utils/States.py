from aiogram.fsm.state import StatesGroup, State


class WhiteList(StatesGroup):
    user = State()
    choose = State()


class TokenList(StatesGroup):
    token = State()


class AdaccountsList(StatesGroup):
    acc = State()
    choose = State()
    settings = State()


