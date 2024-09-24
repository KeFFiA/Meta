import asyncio
import datetime
import os
import shutil
from asyncio import sleep

from aiogram import Router, Bot, F, flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from API_SCRIPTS.Facebook_API import reports_which_is_active
from API_SCRIPTS.GetCourse_API import getcourse_report
from API_SCRIPTS.eWebinar_API import get_all_registrants
from Bot import dialogs
from Bot.bot_keyboards.inline_keyboards import create_white_list_keyboard, create_menu_keyboard, \
    create_help_menu_keyboard, create_help_menu_white_list_keyboard, create_help_menu_tokens_keyboard
from Bot.dialogs import commands
from Bot.utils.States import WhiteList
from Database.database import db
from Bot.bot_keyboards.inline_keyboards import create_fast_report_which_keyboard

user_router = Router()


@user_router.message(Command("start"))
async def start_cmd(message: Message, bot: Bot, state: FSMContext):
    await bot.set_my_commands(commands=commands)
    await message.answer(message.from_user.full_name + dialogs.RU_ru['/start_success'],
                         reply_markup=create_menu_keyboard())
    db.query(
        query="INSERT INTO users (user_id, username, user_name, user_surname) VALUES (%s, %s, %s, %s)",
        values=(
            message.from_user.id, message.from_user.username, message.from_user.first_name,
            message.from_user.last_name,),
        log_level=10,
        msg=f'Пользователь {message.from_user.id} уже записан')
    await state.clear()


@user_router.message(Command('menu'))
async def menu_cmd(message: Message, state: FSMContext):
    await message.answer(text=dialogs.RU_ru['/menu'], reply_markup=create_menu_keyboard())
    await state.clear()


@user_router.message(Command("white_list"))
async def white_list_cmd(message: Message, state: FSMContext):
    keyboard = create_white_list_keyboard()
    await message.answer(text=dialogs.RU_ru['white_list'], reply_markup=keyboard)
    await state.set_state(WhiteList.user)


@user_router.message(Command('fast_report'))
async def fast_report_cmd(message: Message):
    await message.answer(text=dialogs.RU_ru['choose'], reply_markup=create_fast_report_which_keyboard())


@user_router.callback_query(F.data == 'fast_report')
async def fast_report(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['choose'], reply_markup=create_fast_report_which_keyboard())



@user_router.callback_query(F.data == 'fast_report_all')
async def fast_report_all(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['wait_long'], reply_markup=create_menu_keyboard())
    res_1 = await reports_which_is_active()
    res_2 = await get_all_registrants()
    res_3 = await getcourse_report()
    time_sleep = 1505
    while time_sleep > 0:
        if res_1 and res_2 and res_3:
            await call.message.answer(text=dialogs.RU_ru['fast_report_ok'], reply_markup=create_menu_keyboard())
            break
        else:
            await asyncio.sleep(10)
            time_sleep -= 10
            if time_sleep == 5:
                await call.message.answer(text=dialogs.RU_ru['fast_report_bad'], reply_markup=create_menu_keyboard())
                break


@user_router.callback_query(F.data == 'fast_report_facebook')
async def fast_report_facebook(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['wait'])
    res_1 = await reports_which_is_active()
    time_sleep = 1505
    while time_sleep > 0:
        if res_1:
            await call.message.answer(text=dialogs.RU_ru['fast_report_ok'], reply_markup=create_menu_keyboard())
            break
        else:
            await asyncio.sleep(10)
            time_sleep -= 10
            if time_sleep == 5:
                await call.message.answer(text=dialogs.RU_ru['fast_report_bad'], reply_markup=create_menu_keyboard())
                break


@user_router.callback_query(F.data == 'fast_report_ewebinar')
async def fast_report_ewebinar(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['wait_long'])
    res_2 = await get_all_registrants()
    time_sleep = 1505
    while time_sleep > 0:
        if res_2:
            await call.message.answer(text=dialogs.RU_ru['fast_report_ok'], reply_markup=create_menu_keyboard())
            break
        else:
            await asyncio.sleep(10)
            time_sleep -= 10
            if time_sleep == 5:
                await call.message.answer(text=dialogs.RU_ru['fast_report_bad'], reply_markup=create_menu_keyboard())
                break


@user_router.callback_query(F.data == 'fast_report_getcourse')
async def fast_report_getcourse(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['wait_long'])
    res_3 = await getcourse_report()
    time_sleep = 1505
    while time_sleep > 0:
        if res_3:
            await call.message.answer(text=dialogs.RU_ru['fast_report_ok'], reply_markup=create_menu_keyboard())
            break
        else:
            await asyncio.sleep(10)
            time_sleep -= 10
            if time_sleep == 5:
                await call.message.answer(text=dialogs.RU_ru['fast_report_bad'], reply_markup=create_menu_keyboard())
                break


@user_router.message(Command('help'))
async def help_cmd(message: Message):
    await message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'help')
async def help_cmd(call: CallbackQuery):
    await call.message.edit_text(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'help_back')
async def help_back_call(call: CallbackQuery):
    await call.message.edit_text(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'white_list_help')
async def white_list_help_call(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['choose'], reply_markup=create_help_menu_white_list_keyboard())


@user_router.callback_query(F.data == 'add_user_help')
async def add_user_help_call(call: CallbackQuery):
    await call.message.answer(text=dialogs.RU_ru['help_cmd']['add_user'])
    await sleep(10)
    await call.message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'white_list_2_help')
async def white_list_2_help_call(call: CallbackQuery):
    await call.message.answer_photo(photo=FSInputFile(os.path.abspath('../media/white_list_menu.png')),
                                    caption=dialogs.RU_ru['help_cmd']['white_list'])
    await sleep(10)
    await call.message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'tokens_help')
async def tokens_help_call(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['choose'], reply_markup=create_help_menu_tokens_keyboard())


@user_router.callback_query(F.data == 'add_token_help')
async def add_token_help_call(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['help_cmd']['add_token'],
                                 reply_markup=create_help_menu_tokens_keyboard())
    await sleep(10)
    await call.message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'tokens_2_help')
async def tokens_2_help_call(call: CallbackQuery):
    await call.message.edit_text(text=dialogs.RU_ru['help_cmd']['tokens_st1'])
    await sleep(10)
    await call.message.answer_photo(photo=FSInputFile(os.path.abspath('../media/tokens_menu.png')),
                                    caption=dialogs.RU_ru['help_cmd']['tokens_st2'])
    await sleep(10)
    await call.message.answer(text=dialogs.RU_ru['help_cmd']['tokens_st3'])
    await sleep(10)
    await call.message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'main_menu')
async def white_list_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text=dialogs.RU_ru['/menu'], reply_markup=create_menu_keyboard())


@user_router.callback_query(F.data == 'white_list')
async def white_list_call(call: CallbackQuery, state: FSMContext):
    keyboard = create_white_list_keyboard()
    await call.message.edit_text(text=dialogs.RU_ru['white_list'], reply_markup=keyboard)
    await state.set_state(WhiteList.user)


@user_router.callback_query(F.data == 'scheduler_help')
async def scheduler_help(call: CallbackQuery):
    await call.message.edit_text(dialogs.RU_ru['help_cmd']['scheduler'])
    await sleep(10)
    await call.message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'fast_report_help')
async def fast_report_help(call: CallbackQuery):
    await call.message.edit_text(dialogs.RU_ru['help_cmd']['fast_report'])
    await sleep(10)
    await call.message.answer(dialogs.RU_ru['help_cmd']['help_menu'], reply_markup=create_help_menu_keyboard())


@user_router.callback_query(F.data == 'next_page')
async def white_list_next_page(call: CallbackQuery):
    pass


@user_router.callback_query(F.data == 'last_page')
async def white_list_last_page(call: CallbackQuery):
    pass
