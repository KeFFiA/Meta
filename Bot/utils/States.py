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


class SchedulerList(StatesGroup):
    add = State()
    add_st2 = State()
    add_st3 = State()
    task = State()


