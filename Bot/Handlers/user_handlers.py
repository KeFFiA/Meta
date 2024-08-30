import asyncio
import datetime
import shutil
from asyncio import sleep

import os
from aiogram import Router, Bot, F, flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from API_SCRIPTS.Facebook_api import reports_which_is_active
from Bot import dialogs
from Bot.utils.States import WhiteList
from Bot.bot_keyboards.inline_keyboards import create_white_list_keyboard
from Bot.dialogs import commands
from Database.database import db

user_router = Router()


@user_router.message(Command("start"))
async def start_cmd(message: Message, bot: Bot):
    await message.answer(message.from_user.full_name + dialogs.RU_ru['/start_success'])
    await bot.set_my_commands(commands=commands)
    db.query(
        query="INSERT INTO users (user_id, username, user_name, user_surname) VALUES (%s, %s, %s, %s)",
        values=(
            message.from_user.id, message.from_user.username, message.from_user.first_name,
            message.from_user.last_name,),
        log_level=10,
        msg=f'Пользователь {message.from_user.id} уже записан')


@user_router.message(Command("white_list"))
async def white_list_cmd(message: Message, state: FSMContext):
    keyboard = create_white_list_keyboard()
    await message.answer(dialogs.RU_ru['white_list'], reply_markup=keyboard)
    await state.set_state(WhiteList.user)


@user_router.message(Command("fast_report"))
@flags.chat_action("upload_document")
async def fast_report(message: Message):
    file_path = os.path.abspath(f'../temp/{message.from_user.id}/report_{datetime.datetime.today().strftime("%Y-%m-%d")}.csv')
    await message.answer(dialogs.RU_ru['wait'])
    await reports_which_is_active(user_id=message.from_user.id)
    time_sleep = 505
    while time_sleep > 0:
        if os.path.exists(file_path):
            await message.delete()
            await message.answer_document(document=FSInputFile(file_path),
                                          caption=f'{message.from_user.first_name}, вот Ваш файл с отчетом в формате CSV')
            shutil.rmtree(os.path.abspath(f'../temp/{message.from_user.id}'))
            break
        else:
            await asyncio.sleep(10)
            await message.ac
            time_sleep -= 10
            if time_sleep == 5:
                await message.answer('Файл не найден')
                break


@user_router.callback_query(F.data == 'next_page')
async def white_list_next_page(call: CallbackQuery):
    pass


@user_router.callback_query(F.data == 'last_page')
async def white_list_last_page(call: CallbackQuery):
    pass



