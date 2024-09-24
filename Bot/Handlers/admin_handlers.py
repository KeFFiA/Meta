import json
import os
from asyncio import sleep

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from API_SCRIPTS.Facebook_API import check_adacc_facebook
from API_SCRIPTS.eWebinar_API import check_acc_ewebinar
from Bot import dialogs
from Bot.bot_keyboards.inline_keyboards import create_white_list_keyboard, create_token_list_keyboard, \
    create_adacc_settings_keyboard, create_schedulers_keyboard, create_schedulers_add_keyboard, \
    create_scheduler_count_keyboard, create_menu_keyboard
from Bot.utils.States import WhiteList, TokenList, AdaccountsList, SchedulerList
from Bot.utils.scheduler import add_job, get_jobs
from Database.database import db
from Bot.utils.logging_settings import admin_handlers_logger

admin_router = Router()


@admin_router.message(Command("add_user"))
async def add_user_cmd(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    try:
        user_id = command.args.split(" ", maxsplit=1)

    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_user <user_id>"
        )
        return

    if db.query(query="INSERT INTO white_list (user_id) VALUES (%s)", values=(user_id[0],)) == 'Success':
        await message.answer(f'Пользователь {user_id[0]} добавлен!')
    else:
        await message.answer('Пользователь уже добавлен или неверно введен ID')


@admin_router.message(Command("add_token"))
async def add_token_cmd(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы\nПример:\n"
            "/add_token <service> <token>\nВведите /add_token services для просмотра доступных сервисов",
            parse_mode='NONE'
        )
        return
    try:
        try:
            service, token = command.args.split(" ", maxsplit=2)
            if service.lower() == "facebook":
                res = check_adacc_facebook(token)
            elif service.lower() == "getcourse":
                res = check_acc_ewebinar(token)
            elif service.lower() == "ewebinar":
                res = await check_acc_ewebinar(token)

            if res == 200:
                if db.query(query="INSERT INTO tokens (api_token, service) VALUES (%s, %s)",
                            values=(token, service)) == 'Success':
                    await message.answer(f'Токен {service} добавлен!')
                else:
                    await message.answer('Токен уже добавлен')
            elif res == 401:
                await message.answer(text=dialogs.RU_ru['request_facebook']['401'])
            else:
                await message.answer(text=dialogs.RU_ru['request_facebook']['else'],
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [
                                             InlineKeyboardButton(url=f'tg://user?id={config.developer_id}', text='Написать')
                                         ]
                                     ]))
        except:
            service = command.args
            if service == 'services':
                await message.answer(text=dialogs.RU_ru['help_services'])

    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/add_token <service> <token>\nВведите /add_token services для просмотра доступных сервисов",
            parse_mode='NONE'
        )
        return


@admin_router.message(Command("tokens"))
async def token_cmd(message: Message, state: FSMContext):
    keyboard = create_token_list_keyboard()
    await message.answer(dialogs.RU_ru['tokens_list'], reply_markup=keyboard)
    await state.set_state(TokenList.token)


@admin_router.callback_query(F.data.startswith('token_'), TokenList.token)
async def token_list_press_token(call: CallbackQuery, state: FSMContext):
    await state.update_data(token_id=None)
    token_id = call.data.removeprefix('token_')
    token = db.query(query="SELECT api_token FROM tokens WHERE id=%s", values=token_id, fetch='fetchone')[0]

    await state.update_data(token_id=token_id)
    token_accounts = list(
        db.query(query="SELECT acc_name, acc_id, is_active FROM adaccounts WHERE api_token=%s ORDER BY acc_id",
                 values=(token,), fetch='fetchall'))
    text = ''
    count = 1
    builder = InlineKeyboardBuilder()
    buttons = []
    for items in token_accounts:
        acc_name, acc_id, is_active = items
        if is_active:
            active = 'true'
        else:
            active = 'false'
        text += f"""\n\n{count}. {dialogs.RU_ru['adaccount']['name']} {acc_name}
{dialogs.RU_ru['adaccount']['id']} {acc_id}
{dialogs.RU_ru['adaccount']['reports']} {dialogs.RU_ru['adaccount']['is_active'][f'{active}']}"""
        try:
            buttons.append(InlineKeyboardButton(
                text=str(count),
                callback_data=acc_id
            ))
        except:
            pass

        count += 1

    builder.row(*buttons, width=3)
    last_btn = InlineKeyboardButton(callback_data='act_back_to_token', text=dialogs.RU_ru['navigation']['back'])
    last_btns = InlineKeyboardMarkup(inline_keyboard=[[last_btn]])
    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))
    keyboard = builder.as_markup()

    await call.message.edit_text(text=text, reply_markup=keyboard)
    await state.set_state(AdaccountsList.acc)


@admin_router.callback_query(F.data.startswith('act_'), AdaccountsList.acc)
async def token_list_press_token(call: CallbackQuery, state: FSMContext):
    choose = call.data
    if choose == 'act_back_to_token':
        keyboard = create_token_list_keyboard()
        await call.message.edit_text(dialogs.RU_ru['tokens_list'], reply_markup=keyboard)
        await state.update_data(token_id=None, account=None)
        await state.set_state(TokenList.token)
    else:
        await state.update_data(account=choose)

        data = list(db.query(query="SELECT acc_name, acc_id, is_active FROM adaccounts WHERE acc_id=%s",
                             values=(choose,), fetch='fetchone'))

        inline_btn_reports_acc = InlineKeyboardButton(callback_data='acc_btn_reports',
                                                      text=dialogs.RU_ru['navigation']['reports'])
        inline_btn_activate_acc = InlineKeyboardButton(callback_data='acc_btn_activate',
                                                       text=dialogs.RU_ru['navigation']['activate'])
        inline_btn_deactivate_acc = InlineKeyboardButton(callback_data='acc_btn_deactivate',
                                                         text=dialogs.RU_ru['navigation']['deactivate'])
        inline_btn_back_acc = InlineKeyboardButton(callback_data='acc_btn_back_to_acc',
                                                   text=dialogs.RU_ru['navigation']['back'])

        acc_name, acc_id, is_active = data
        if is_active:
            active = 'true'
            inline_kb_acc = InlineKeyboardMarkup(inline_keyboard=[
                [inline_btn_deactivate_acc], [inline_btn_reports_acc], [inline_btn_back_acc]
            ])
        else:
            active = 'false'
            inline_kb_acc = InlineKeyboardMarkup(inline_keyboard=[
                [inline_btn_activate_acc], [inline_btn_reports_acc], [inline_btn_back_acc]
            ])

        await call.message.edit_text(text=f"""<b>{dialogs.RU_ru['adaccount']['name']} {acc_name}
{dialogs.RU_ru['adaccount']['id']} {acc_id}</b>

{dialogs.RU_ru['adaccount']['reports']} {dialogs.RU_ru['adaccount']['is_active'][active]}""",
                                     reply_markup=inline_kb_acc)
        await state.update_data(acc_id=acc_id, acc_name=acc_name)
        await state.set_state(AdaccountsList.choose)


@admin_router.callback_query(F.data.startswith('acc_btn'), AdaccountsList.choose)
async def acc_press_btn(call: CallbackQuery, state: FSMContext):
    if call.data == 'acc_btn_back_to_acc':
        token_id = await state.get_data()
        token = \
            db.query(query="SELECT api_token FROM tokens WHERE id=%s", values=token_id['token_id'], fetch='fetchone')[0]

        token_accounts = list(
            db.query(query="SELECT acc_name, acc_id, is_active FROM adaccounts WHERE api_token=%s ORDER BY acc_id",
                     values=(token,), fetch='fetchall'))
        text = ''
        count = 1
        builder = InlineKeyboardBuilder()
        buttons = []
        for items in token_accounts:
            acc_name, acc_id, is_active = items
            if is_active:
                active = 'true'
            else:
                active = 'false'
            text += f"""\n\n{count}. {dialogs.RU_ru['adaccount']['name']} {acc_name}
{dialogs.RU_ru['adaccount']['id']} {acc_id}

{dialogs.RU_ru['adaccount']['reports']} {dialogs.RU_ru['adaccount']['is_active'][f'{active}']}"""
            try:
                buttons.append(InlineKeyboardButton(
                    text=str(count),
                    callback_data=acc_id
                ))
            except:
                pass

            count += 1

        builder.row(*buttons, width=3)
        last_btn = InlineKeyboardButton(callback_data='act_back_to_token', text=dialogs.RU_ru['navigation']['back'])
        last_btns = InlineKeyboardMarkup(inline_keyboard=[[last_btn]])
        builder.attach(InlineKeyboardBuilder.from_markup(last_btns))
        keyboard = builder.as_markup()

        await call.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(AdaccountsList.acc)

    inline_btn_reports_acc = InlineKeyboardButton(callback_data='acc_btn_reports',
                                                  text=dialogs.RU_ru['navigation']['reports'])
    inline_btn_activate_acc = InlineKeyboardButton(callback_data='acc_btn_activate',
                                                   text=dialogs.RU_ru['navigation']['activate'])
    inline_btn_deactivate_acc = InlineKeyboardButton(callback_data='acc_btn_deactivate',
                                                     text=dialogs.RU_ru['navigation']['deactivate'])
    inline_btn_back_acc = InlineKeyboardButton(callback_data='acc_btn_back_to_acc',
                                               text=dialogs.RU_ru['navigation']['back'])
    data = await state.get_data()
    if call.data == 'acc_btn_activate':
        db.query(query="UPDATE adaccounts SET is_active=true WHERE acc_id=%s",
                 values=(data['acc_id'],))
        active = 'true'

        inline_kb_acc = InlineKeyboardMarkup(inline_keyboard=[
            [inline_btn_deactivate_acc], [inline_btn_reports_acc], [inline_btn_back_acc]
        ])

        await call.message.edit_text(text=f"""<b>{dialogs.RU_ru['adaccount']['name']} {data['acc_name']}
{dialogs.RU_ru['adaccount']['id']} {data['acc_id']}</b>

{dialogs.RU_ru['adaccount']['reports']} {dialogs.RU_ru['adaccount']['is_active'][active]}""",
                                     reply_markup=inline_kb_acc)

    if call.data == 'acc_btn_deactivate':
        db.query(query="UPDATE adaccounts SET is_active=false WHERE acc_id=%s",
                 values=(data['acc_id'],))
        active = 'false'

        inline_kb_acc = InlineKeyboardMarkup(inline_keyboard=[
            [inline_btn_activate_acc], [inline_btn_reports_acc], [inline_btn_back_acc]
        ])

        await call.message.edit_text(text=f"""<b>{dialogs.RU_ru['adaccount']['name']} {data['acc_name']}
{dialogs.RU_ru['adaccount']['id']} {data['acc_id']}</b>

{dialogs.RU_ru['adaccount']['reports']} {dialogs.RU_ru['adaccount']['is_active'][active]}""",
                                     reply_markup=inline_kb_acc)

    if call.data == 'acc_btn_reports':
        keyboard = create_adacc_settings_keyboard()
        count = 1
        text = f"""<b>{dialogs.RU_ru['adaccount']['name']} {data['acc_name']}
{dialogs.RU_ru['adaccount']['id']} {data['acc_id']}</b>\n\n"""
        for i in dialogs.RU_ru['adacc_settings']['fields']:
            active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                  fetch='fetchone')[0])

            text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

            count += 1
        level, date_preset, increment = (
            db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                     values=(data['acc_id'],),
                     fetch='fetchall'))[0]
        text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""
        await call.message.edit_text(text=text, reply_markup=keyboard)
        await state.update_data(text=text)

        await state.set_state(AdaccountsList.settings)


@admin_router.callback_query(F.data, AdaccountsList.settings)
async def acc_press_settings_btn(call: CallbackQuery, state: FSMContext):
    choose = call.data
    data = await state.get_data()
    keyboard = create_adacc_settings_keyboard()
    text = f"""<b>{dialogs.RU_ru['adaccount']['name']} {data['acc_name']}
{dialogs.RU_ru['adaccount']['id']} {data['acc_id']}</b>\n\n"""
    try:
        if choose == 'activate_all':
            db.query(query="""UPDATE adaccounts SET account_name = TRUE, account_id = TRUE, campaign_name = TRUE, 
            campaign_id = TRUE, adset_name = TRUE, adset_id = TRUE, ad_name = TRUE, ad_id = TRUE, impressions = TRUE, 
            frequency = TRUE, clicks = TRUE, unique_clicks = TRUE, spend = TRUE, reach = TRUE, cpp = TRUE, cpm = TRUE, 
            unique_link_clicks_ctr = TRUE, ctr = TRUE, unique_ctr = TRUE, cpc = TRUE, cost_per_unique_click = TRUE, 
            objective = TRUE, buying_type = TRUE, created_time = TRUE WHERE acc_id = %s;""",
                     values=(data['acc_id'],))

            count = 1

            for i in dialogs.RU_ru['adacc_settings']['fields']:
                active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                      fetch='fetchone')[0])

                text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                count += 1
            level, date_preset, increment = (
                db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                         values=(data['acc_id'],),
                         fetch='fetchall'))[0]
            text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

            await call.message.edit_text(text=text, reply_markup=keyboard)

        elif choose == 'deactivate_all':
            db.query(query="""UPDATE adaccounts SET account_name = FALSE, account_id = FALSE, campaign_name = FALSE, 
            campaign_id = FALSE, adset_name = FALSE, adset_id = FALSE, ad_name = FALSE, ad_id = FALSE, 
            impressions = FALSE, frequency = FALSE, clicks = FALSE, unique_clicks = FALSE, spend = FALSE, reach = FALSE, 
            cpp = FALSE, cpm = FALSE, unique_link_clicks_ctr = FALSE, ctr = FALSE, unique_ctr = FALSE, cpc = FALSE, 
            cost_per_unique_click = FALSE, objective = FALSE, buying_type = FALSE, created_time = FALSE 
            WHERE acc_id = %s;""",
                     values=(data['acc_id'],))

            count = 1

            for i in dialogs.RU_ru['adacc_settings']['fields']:
                active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                      fetch='fetchone')[0])

                text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                count += 1
            level, date_preset, increment = (
                db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                         values=(data['acc_id'],),
                         fetch='fetchall'))[0]
            text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

            await call.message.edit_text(text=text, reply_markup=keyboard)

        elif choose == 'back':
            data_db = list(db.query(query="SELECT acc_name, acc_id, is_active FROM adaccounts WHERE acc_id=%s",
                                    values=(data['account'],), fetch='fetchone'))

            inline_btn_reports_acc = InlineKeyboardButton(callback_data='acc_btn_reports',
                                                          text=dialogs.RU_ru['navigation']['reports'])
            inline_btn_activate_acc = InlineKeyboardButton(callback_data='acc_btn_activate',
                                                           text=dialogs.RU_ru['navigation']['activate'])
            inline_btn_deactivate_acc = InlineKeyboardButton(callback_data='acc_btn_deactivate',
                                                             text=dialogs.RU_ru['navigation']['deactivate'])
            inline_btn_back_acc = InlineKeyboardButton(callback_data='acc_btn_back_to_acc',
                                                       text=dialogs.RU_ru['navigation']['back'])
            acc_name, acc_id, is_active = data_db
            if is_active:
                active = 'true'
                inline_kb_acc = InlineKeyboardMarkup(inline_keyboard=[
                    [inline_btn_deactivate_acc], [inline_btn_reports_acc], [inline_btn_back_acc]
                ])
            else:
                active = 'false'
                inline_kb_acc = InlineKeyboardMarkup(inline_keyboard=[
                    [inline_btn_activate_acc], [inline_btn_reports_acc], [inline_btn_back_acc]
                ])

            await call.message.edit_text(text=f"""<b>{dialogs.RU_ru['adaccount']['name']} {acc_name}
{dialogs.RU_ru['adaccount']['id']} {acc_id}</b>
{dialogs.RU_ru['adaccount']['reports']} {dialogs.RU_ru['adaccount']['is_active'][active]}""",
                                         reply_markup=inline_kb_acc)
            await state.set_state(AdaccountsList.choose)

        elif choose == 'increment':
            increment_list = [1, 7, 15, 30, 90]
            increment_db = db.query(query="SELECT increment FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                    fetch='fetchone')[0]
            index = increment_list.index(increment_db) + 1
            try:
                db.query(query="UPDATE adaccounts SET increment=%s WHERE acc_id=%s",
                         values=(increment_list[index], data['acc_id']))
            except:
                db.query(query="UPDATE adaccounts SET increment=1 WHERE acc_id=%s",
                         values=(data['acc_id'],))
            finally:
                count = 1

                for i in dialogs.RU_ru['adacc_settings']['fields']:
                    active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                          fetch='fetchone')[0])

                    text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                    count += 1
                level, date_preset, increment = (
                    db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                             values=(data['acc_id'],),
                             fetch='fetchall'))[0]
                text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

                await call.message.edit_text(text=text, reply_markup=keyboard)
        elif choose == 'level':
            level_list = ['ad', 'adset', 'campaign', 'account']

            level_db = db.query(query="SELECT level FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                fetch='fetchone')[0]
            index = level_list.index(level_db) + 1
            try:
                db.query(query="UPDATE adaccounts SET level=%s WHERE acc_id=%s",
                         values=(level_list[index], data['acc_id']))
            except:
                db.query(query="UPDATE adaccounts SET level='ad' WHERE acc_id=%s",
                         values=(data['acc_id'],))
            finally:
                count = 1

                for i in dialogs.RU_ru['adacc_settings']['fields']:
                    active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                          fetch='fetchone')[0])

                    text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                    count += 1
                level, date_preset, increment = (
                    db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                             values=(data['acc_id'],),
                             fetch='fetchall'))[0]
                text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

                await call.message.edit_text(text=text, reply_markup=keyboard)

        elif choose == 'preset':
            preset_list = ['today', 'yesterday', 'this_week', 'last_week', 'this_month', 'last_month',
                           'this_quarter', 'last_quarter', 'this_year', 'last_year', 'maximum']
            preset_db = db.query(query="SELECT date_preset FROM adaccounts WHERE acc_id=%s",
                                 values=(data['acc_id'],), fetch='fetchone')[0]
            index = preset_list.index(preset_db) + 1

            try:
                db.query(query="UPDATE adaccounts SET date_preset=%s WHERE acc_id=%s",
                         values=(preset_list[index], data['acc_id']))
            except:
                db.query(query="UPDATE adaccounts SET date_preset='today' WHERE acc_id=%s",
                         values=(data['acc_id'],))
            finally:
                count = 1

                for i in dialogs.RU_ru['adacc_settings']['fields']:
                    active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                          fetch='fetchone')[0])

                    text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                    count += 1
                level, date_preset, increment = (
                    db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                             values=(data['acc_id'],),
                             fetch='fetchall'))[0]
                text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

                await call.message.edit_text(text=text, reply_markup=keyboard)
        else:
            active = str(db.query(f"SELECT {choose} FROM adaccounts WHERE acc_id=%s",
                                  values=(data['acc_id'],), fetch='fetchone')[0]).lower()
            if active == 'true':
                db.query(query=f'UPDATE adaccounts SET {choose} = FALSE WHERE acc_id=%s',
                         values=(data['acc_id'],))
                count = 1

                for i in dialogs.RU_ru['adacc_settings']['fields']:
                    active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                          fetch='fetchone')[0])

                    text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                    count += 1
                level, date_preset, increment = (
                    db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                             values=(data['acc_id'],),
                             fetch='fetchall'))[0]
                text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

                await call.message.edit_text(text=text, reply_markup=keyboard)
            else:
                db.query(query=f'UPDATE adaccounts SET {choose} = TRUE WHERE acc_id=%s',
                         values=(data['acc_id'],))
                count = 1

                for i in dialogs.RU_ru['adacc_settings']['fields']:
                    active = str(db.query(query=f"SELECT {i} FROM adaccounts WHERE acc_id=%s", values=(data['acc_id'],),
                                          fetch='fetchone')[0])

                    text += f"{count}. {dialogs.RU_ru['adacc_settings']['fields'][i]} {dialogs.RU_ru['adaccount']['is_active'][active.lower()]}\n"

                    count += 1
                level, date_preset, increment = (
                    db.query(query="SELECT level, date_preset, increment FROM adaccounts WHERE acc_id=%s",
                             values=(data['acc_id'],),
                             fetch='fetchall'))[0]
                text += f"""\n{dialogs.RU_ru['adacc_settings']['date_preset']['text']} {dialogs.RU_ru['adacc_settings']['date_preset'][date_preset]}
{dialogs.RU_ru['adacc_settings']['level']['text']} {dialogs.RU_ru['adacc_settings']['level'][level]}
{dialogs.RU_ru['adacc_settings']['increment']['text']} {dialogs.RU_ru['adacc_settings']['increment'][increment]}"""

                await call.message.edit_text(text=text, reply_markup=keyboard)
    except:
        await call.answer()
        pass


@admin_router.callback_query(F.data.startswith('white_'), WhiteList.user)
async def white_list_press_user(call: CallbackQuery, state: FSMContext):
    user_id = call.data.removeprefix('white_')
    await state.update_data(user_id=user_id)
    user_data = list(db.query(query="SELECT user_name, user_surname, username, user_id FROM users WHERE user_id=%s",
                              values=(int(user_id),), fetch='fetchall')[0])

    is_admin = db.query(query="SELECT admin FROM white_list WHERE user_id=%s",
                        values=(int(user_id),), fetch='fetchone')[0]

    inline_btn_delete_user = InlineKeyboardButton(callback_data='white_btn_delete_from_white_list',
                                                  text=dialogs.RU_ru['navigation']['delete'])
    inline_btn_upgrade_user = InlineKeyboardButton(callback_data='white_btn_upgrade_to_admin',
                                                   text=dialogs.RU_ru['navigation']['upgrade'])
    inline_btn_downgrade_user = InlineKeyboardButton(callback_data='white_btn_downgrade_to_user',
                                                     text=dialogs.RU_ru['navigation']['downgrade'])
    inline_btn_back_user = InlineKeyboardButton(callback_data='white_btn_back_to_white_list',
                                                text=dialogs.RU_ru['navigation']['back'])
    inline_btn_acc_user = InlineKeyboardButton(url=f'tg://user?id={user_id}',
                                               text=dialogs.RU_ru['navigation']['message'])
    inline_btn_back_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')

    if is_admin:
        admin = 'true'
        inline_kb_user = InlineKeyboardMarkup(inline_keyboard=[
            [inline_btn_acc_user],
            [inline_btn_downgrade_user, inline_btn_delete_user],
            [inline_btn_back_user],
            [inline_btn_back_menu]
        ])
    else:
        admin = 'false'
        inline_kb_user = InlineKeyboardMarkup(inline_keyboard=[
            [inline_btn_acc_user],
            [inline_btn_upgrade_user, inline_btn_delete_user],
            [inline_btn_back_user],
            [inline_btn_back_menu]
        ])
    await state.update_data(user_data=user_data, admin=admin)
    if user_data[1] is None:
        user_data[1] = ''
    await call.message.edit_text(f"""{dialogs.RU_ru['user']['name']} {user_data[0]} {user_data[1]}
{dialogs.RU_ru['user']['username']} {user_data[2]}
{dialogs.RU_ru['user']['id']} <code>{user_data[3]}</code>

{dialogs.RU_ru['user']['admin']} {dialogs.RU_ru['user']['is_admin'][admin]}""",
                                 reply_markup=inline_kb_user, parse_mode='HTML')
    await state.set_state(WhiteList.choose)


@admin_router.callback_query(F.data.startswith('white_btn'), WhiteList.choose)
async def white_choose(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    choose = call.data

    inline_btn_delete_user = InlineKeyboardButton(callback_data='white_btn_delete_from_white_list',
                                                  text=dialogs.RU_ru['navigation']['delete'])
    inline_btn_upgrade_user = InlineKeyboardButton(callback_data='white_btn_upgrade_to_admin',
                                                   text=dialogs.RU_ru['navigation']['upgrade'])
    inline_btn_downgrade_user = InlineKeyboardButton(callback_data='white_btn_downgrade_to_user',
                                                     text=dialogs.RU_ru['navigation']['downgrade'])
    inline_btn_back_user = InlineKeyboardButton(callback_data='white_btn_back_to_white_list',
                                                text=dialogs.RU_ru['navigation']['back'])
    inline_btn_acc_user = InlineKeyboardButton(url=f'tg://user?id={data['user_id']}',
                                               text=dialogs.RU_ru['navigation']['message'])
    inline_btn_back_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')

    if choose == 'white_btn_delete_from_white_list':
        db.query(query="DELETE FROM white_list WHERE user_id=%s",
                 values=(int(data['user_id']),))
        await call.answer(text='Пользователь удален', show_alert=True)
        await state.update_data(user_id='', user_data='')
        keyboard = create_white_list_keyboard()
        await call.message.edit_text(dialogs.RU_ru['white_list'], reply_markup=keyboard)
        await state.set_state(WhiteList.user)

    elif choose == 'white_btn_upgrade_to_admin':
        db.query(query="UPDATE white_list SET admin=true WHERE user_id=%s",
                 values=(int(data['user_id']),))
        await call.answer(text='Пользователь повышен до администратора', show_alert=True)

        inline_kb_user = InlineKeyboardMarkup(inline_keyboard=[
            [inline_btn_acc_user],
            [inline_btn_downgrade_user, inline_btn_delete_user],
            [inline_btn_back_user],
            [inline_btn_back_menu]
        ])

        await call.message.edit_text(text=f"""
{dialogs.RU_ru['user']['name']} {data['user_data'][0]} {data['user_data'][1]}
{dialogs.RU_ru['user']['username']} {data['user_data'][2]}
{dialogs.RU_ru['user']['id']} <code>{data['user_data'][3]}</code>

{dialogs.RU_ru['user']['admin']} {dialogs.RU_ru['user']['is_admin']['true']}""", reply_markup=inline_kb_user)

    elif choose == 'white_btn_downgrade_to_user':
        db.query(query="UPDATE white_list SET admin=false WHERE user_id=%s",
                 values=(int(data['user_id']),))

        await call.answer(text='Пользователь понижен до пользователя', show_alert=True)
        inline_kb_user = InlineKeyboardMarkup(inline_keyboard=[
            [inline_btn_acc_user],
            [inline_btn_upgrade_user, inline_btn_delete_user],
            [inline_btn_back_user],
            [inline_btn_back_menu]
        ])

        await call.message.edit_text(text=f"""
{dialogs.RU_ru['user']['name']} {data['user_data'][0]} {data['user_data'][1]}
{dialogs.RU_ru['user']['username']} {data['user_data'][2]}
{dialogs.RU_ru['user']['id']} <code>{data['user_data'][3]}</code>

{dialogs.RU_ru['user']['admin']} {dialogs.RU_ru['user']['is_admin']['false']}""", reply_markup=inline_kb_user)

    elif choose == 'white_btn_back_to_white_list':
        await state.update_data(user_id='', user_data='')
        keyboard = create_white_list_keyboard()
        await call.message.edit_text(dialogs.RU_ru['white_list'], reply_markup=keyboard)
        await state.set_state(WhiteList.user)


@admin_router.message(Command('scheduler'))
async def scheduler_command(message: Message):
    data = await get_jobs()
    if not data:
        button = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['add'], callback_data='edit_scheduler')
        main_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
        keyboard_1 = InlineKeyboardMarkup(inline_keyboard=[
            [button],
            [main_menu]
        ])
        await message.answer(dialogs.RU_ru['scheduler']['None'], reply_markup=keyboard_1)
    else:
        keyboard = create_schedulers_keyboard()
        text = ''
        data = await get_jobs()
        count = 1
        for items in data:
            job_ids, time = items
            job_id = job_ids.removesuffix(f'_{count}')
            if ':' in time:
                hour, minute = time.split(':')
            else:
                hour, minute = time.split('.')
            text += f'{job_id} - {hour}:{minute}\n\n'
            count += 1

        await message.answer(f'{dialogs.RU_ru['scheduler']['notNone']}\n\n{text}', reply_markup=keyboard)


@admin_router.callback_query(F.data == 'edit_scheduler')
async def scheduler_add(call: CallbackQuery):
    keyboard = create_schedulers_add_keyboard()
    await call.message.edit_text(text=dialogs.RU_ru['scheduler']['which'], reply_markup=keyboard)


@admin_router.callback_query(F.data.startswith('scheduler_edit_'))
async def scheduler_add_st_1(call: CallbackQuery, state: FSMContext):
    data_1 = call.data
    data = data_1.removeprefix('scheduler_edit_')
    await state.update_data(choose=data, count=0)

    await call.message.edit_text(text=dialogs.RU_ru['scheduler']['add_text'],
                                 reply_markup=create_scheduler_count_keyboard(count=-1, data=data))
    await state.set_state(SchedulerList.add_st2)


@admin_router.callback_query(SchedulerList.add_st2)
async def scheduler_add_st_2(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    counter = data['count']

    if call.data == f'{data['choose']}_add':
        try:
            counter += 1
            await state.update_data(count=counter)
            await call.message.edit_text(text=dialogs.RU_ru['scheduler']['add_text'],
                                         reply_markup=create_scheduler_count_keyboard(count=counter,
                                                                                      data=data['choose']))
        except:
            await call.answer()
            pass
        finally:
            await state.set_state(SchedulerList.add_st2)

    if call.data == f'{data['choose']}_del':
        try:
            counter -= 1
            if counter < 0:
                counter = 0
            await state.update_data(count=counter)
            await call.message.edit_text(text=dialogs.RU_ru['scheduler']['add_text'],
                                         reply_markup=create_scheduler_count_keyboard(count=counter,
                                                                                      data=data['choose']))
        except:
            await call.answer()
            pass
        finally:
            await state.set_state(SchedulerList.add_st2)

    if call.data.startswith('scheduler_'):
        await state.update_data(task=call.data)
        button = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['back'], callback_data='scheduler2_back')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
        await call.message.edit_text(text=dialogs.RU_ru['scheduler']['task_add'], reply_markup=keyboard)
        await state.set_state(SchedulerList.task)

    if call.data == 'done':
        try:
            os.mkdir('./temp/')
        except FileExistsError:
            pass
        temp_dir = os.path.abspath('./temp/')
        file_name = os.path.join(temp_dir, f'{data['choose']}_scheduler.json')
        try:
            with open(file_name, 'r') as file:
                try:
                    file_data = json.load(file)
                except json.JSONDecodeError as _ex:
                    await call.message.edit_text(dialogs.RU_ru['scheduler']['scheduler_add_error'])
                    await sleep(5)
                    await call.message.answer(text=dialogs.RU_ru['/menu'], reply_markup=create_menu_keyboard())
                    admin_handlers_logger.error(msg=f'Add scheduler failed with error: {_ex}')

                counter = 1
                text = ''
                try:
                    for item in file_data:
                        scheduler = f'{data['choose']}_scheduler_{counter}'
                        time = item[scheduler]
                        await add_job(scheduler, time)
                        text += f'{scheduler} - {time}\n\n'
                        counter += 1
                except Exception as _ex:
                    await state.clear()
                    await call.message.edit_text(dialogs.RU_ru['scheduler']['scheduler_add_error_None'])
                    await sleep(5)
                    keyboard = create_schedulers_add_keyboard()
                    await call.message.edit_text(text=dialogs.RU_ru['scheduler']['which'], reply_markup=keyboard)

                with open(file_name, 'w') as f:
                    f.write('')

                await call.message.edit_text(text=f'{dialogs.RU_ru['scheduler']['scheduler_add_done']}{text}')
                await sleep(5)
                await state.clear()
                await call.message.answer(text=dialogs.RU_ru['/menu'], reply_markup=create_menu_keyboard())

        except FileNotFoundError as _ex:
            await call.message.edit_text(dialogs.RU_ru['scheduler']['scheduler_add_error'])
            await sleep(5)
            await call.message.answer(text=dialogs.RU_ru['/menu'], reply_markup=create_menu_keyboard())
            admin_handlers_logger.error(msg=f'Add scheduler failed with error: {_ex}')

    if call.data == 'scheduler1_back':
        try:
            os.mkdir('./temp/')
        except FileExistsError:
            pass
        temp_dir = os.path.abspath(f'./temp/')
        file_name = os.path.join(temp_dir, f'{data['choose']}_scheduler.json')
        with open(file_name, 'w') as f:
            f.write('')
        await state.clear()
        keyboard = create_schedulers_add_keyboard()
        await call.message.edit_text(text=dialogs.RU_ru['scheduler']['which'], reply_markup=keyboard)


@admin_router.message(SchedulerList.task)
@admin_router.callback_query(SchedulerList.task)
async def add_task(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    task = data['task']
    choose = data['choose']
    if isinstance(event, CallbackQuery):
        counter = data['count']
        await event.message.edit_text(text=dialogs.RU_ru['scheduler']['add_text'],
                                      reply_markup=create_scheduler_count_keyboard(count=counter,
                                                                                   data=data['choose']))
    elif isinstance(event, Message):
        text = {f'{choose}_{task}': event.text}
        temp_dir = os.path.abspath(f'./temp/')
        file_name = os.path.join(temp_dir, f'{choose}_scheduler.json')
        os.makedirs(temp_dir, exist_ok=True)

        file_data = []

        try:
            with open(file_name, 'r') as file:
                try:
                    file_data = json.load(file)
                except json.JSONDecodeError:
                    file_data = []
        except FileNotFoundError:
            pass
        existing_item = None
        for item in file_data:
            if task in item:
                existing_item = item
                break

        if existing_item is not None:
            existing_item[task] = event.text
        else:
            file_data.append(text)

        with open(file_name, 'w') as file:
            json.dump(file_data, file, indent=4)

        await event.answer(text=dialogs.RU_ru['scheduler']['add_text'],
                              reply_markup=create_scheduler_count_keyboard(count=data['count'], data=data['choose']))

    await state.update_data(task='')
    await state.set_state(SchedulerList.add_st2)


@admin_router.callback_query(F.data == 'tokens')
async def tokens_call(call: CallbackQuery, state: FSMContext):
    keyboard = create_token_list_keyboard()
    await call.message.edit_text(dialogs.RU_ru['tokens_list'], reply_markup=keyboard)
    await state.set_state(TokenList.token)


@admin_router.callback_query(F.data == 'scheduler')
async def scheduler_call(call: CallbackQuery):
    data = await get_jobs()
    if not data:
        button = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['add'], callback_data='edit_scheduler')
        main_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
        button_markup = InlineKeyboardMarkup(inline_keyboard=[
            [button],
            [main_menu]
        ])
        await call.message.edit_text(dialogs.RU_ru['scheduler']['None'], reply_markup=button_markup)
    else:
        keyboard = create_schedulers_keyboard()
        text = ''
        data = await get_jobs()
        count = 1
        for items in data:
            job_ids, time = items
            if ':' in time:
                hour, minute = time.split(':')
            else:
                hour, minute = time.split('.')
            text += f'{job_ids} - {hour}:{minute}\n\n'
            count += 1

        await call.message.edit_text(f'{dialogs.RU_ru['scheduler']['notNone']}\n\n{text}', reply_markup=keyboard)


@admin_router.callback_query(F.data == 'delete_scheduler')
async def delete_scheduler_call(call: CallbackQuery):
    db.query(query="DELETE FROM scheduled_jobs")
    button = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['add'], callback_data='edit_scheduler')
    main_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
    button_markup = InlineKeyboardMarkup(inline_keyboard=[
        [button],
        [main_menu]
    ])
    await call.message.edit_text(dialogs.RU_ru['scheduler']['None'], reply_markup=button_markup)


@admin_router.callback_query(F.data == 'scheduler_back')
async def scheduler_back_call(call: CallbackQuery):
    data = await get_jobs()
    if not data:
        button = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['add'], callback_data='edit_scheduler')
        main_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
        button_markup = InlineKeyboardMarkup(inline_keyboard=[
            [button],
            [main_menu]
        ])
        await call.message.edit_text(dialogs.RU_ru['scheduler']['None'], reply_markup=button_markup)
    else:
        keyboard = create_schedulers_keyboard()
        text = ''
        data = await get_jobs()
        count = 1
        for items in data:
            job_ids, time = items
            job_id = job_ids.removesuffix(f'_{count}')
            hour, minute = time.split(':')
            text += f'{job_id} - {hour}:{minute}\n\n'
            count += 1

        await call.message.edit_text(f'{dialogs.RU_ru['scheduler']['notNone']}\n\n{text}', reply_markup=keyboard)


@admin_router.callback_query(F.data == 'scheduler1_back')
async def scheduler_back_1_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = create_schedulers_add_keyboard()
    await call.message.edit_text(text=dialogs.RU_ru['scheduler']['which'], reply_markup=keyboard)
