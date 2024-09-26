import json
import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from Bot import dialogs
from Database.database_query import white_list, token_list


def create_white_list_keyboard():
    builder = InlineKeyboardBuilder()
    button = white_list()
    buttons = []
    for data, text in button.items():
        try:
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=data
            ))
        except:
            pass

    builder.row(*buttons, width=1)
    last_btn_1 = InlineKeyboardButton(callback_data='next_page', text='-->')
    last_btn_2 = InlineKeyboardButton(callback_data='last_page', text='<--')
    last_btn_3 = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
    last_btns = InlineKeyboardMarkup(inline_keyboard=[[last_btn_2, last_btn_1], [last_btn_3]])
    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))
    return builder.as_markup()


def create_token_list_keyboard():
    builder = InlineKeyboardBuilder()
    button = token_list()
    buttons = []
    for data, text in button.items():
        try:
            buttons.append(InlineKeyboardButton(
                text=f"[{text['service']}]  " + text['token'][:25],
                callback_data=data
            ))
        except:
            pass

    builder.row(*buttons, width=1)
    last_btn_1 = InlineKeyboardButton(callback_data='next_page', text='-->')
    last_btn_2 = InlineKeyboardButton(callback_data='last_page', text='<--')
    last_btn_3 = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
    last_btns = InlineKeyboardMarkup(inline_keyboard=[[last_btn_2, last_btn_1], [last_btn_3]])
    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))
    return builder.as_markup()


def create_adacc_settings_keyboard():
    builder = InlineKeyboardBuilder()
    button = dialogs.RU_ru['adacc_settings']['fields']
    buttons = []
    count = 1
    for i in button:
        try:
            buttons.append(InlineKeyboardButton(
                text=str(count),
                callback_data=i
            ))
            count += 1
        except:
            pass

    builder.row(*buttons, width=5)
    activate_all_btn = InlineKeyboardButton(callback_data='activate_all',
                                            text=dialogs.RU_ru['navigation']['activate_all'])
    deactivate_all_btn = InlineKeyboardButton(callback_data='deactivate_all',
                                              text=dialogs.RU_ru['navigation']['deactivate_all'])
    back_btn = InlineKeyboardButton(callback_data='back',
                                    text=dialogs.RU_ru['navigation']['back'])
    level_btn = InlineKeyboardButton(callback_data='level',
                                     text=dialogs.RU_ru['navigation']['level'])
    preset_btn = InlineKeyboardButton(callback_data='preset',
                                      text=dialogs.RU_ru['navigation']['date_preset'])
    increment_btn = InlineKeyboardButton(callback_data='increment',
                                         text=dialogs.RU_ru['navigation']['increment'])
    main_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')

    last_btns = InlineKeyboardMarkup(inline_keyboard=[
        [preset_btn, level_btn, increment_btn],
        [activate_all_btn, back_btn, deactivate_all_btn],
        [main_menu]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))

    return builder.as_markup()


def create_schedulers_keyboard():
    delete = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['delete'],
                                  callback_data='delete_scheduler')
    edit = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['edit_scheduler'], callback_data='edit_scheduler')
    back_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [edit],
        [delete],
        [back_menu]
    ])

    return keyboard


def create_schedulers_add_keyboard():
    button_add_facebook = InlineKeyboardButton(text=dialogs.RU_ru['scheduler']['facebook'],
                                               callback_data='scheduler_edit_facebook')
    button_add_eWebinar = InlineKeyboardButton(text=dialogs.RU_ru['scheduler']['ewebinar'],
                                               callback_data='scheduler_edit_ewebinar')
    button_add_getcourse = InlineKeyboardButton(text=dialogs.RU_ru['scheduler']['getcourse'],
                                                callback_data='scheduler_edit_getcourse')

    back_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['back'], callback_data='scheduler_back')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_add_facebook],
        [button_add_eWebinar],
        [button_add_getcourse],
        [back_menu]
    ])
    return keyboard


def create_menu_keyboard():
    white_list_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['white_list'], callback_data='white_list')
    tokens = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['token'], callback_data='tokens')
    scheduler = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['scheduler'], callback_data='scheduler')
    fast_report = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['fast_report'], callback_data='fast_report')
    logs = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['logs'], callback_data='logs')
    helper = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['help'], callback_data='help')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [white_list_btn],
        [tokens],
        [scheduler],
        [fast_report],
        [logs],
        [helper]
    ])

    return keyboard


def create_help_menu_keyboard():
    white_list_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['white_list'],
                                          callback_data='white_list_help')
    tokens = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['token'], callback_data='tokens_help')
    scheduler = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['scheduler'], callback_data='scheduler_help')
    fast_report = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['fast_report'],
                                       callback_data='fast_report_help')
    back_menu = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [white_list_btn],
        [tokens],
        [scheduler],
        [fast_report],
        [back_menu]
    ])

    return keyboard


def create_help_menu_white_list_keyboard():
    add_user_btn = InlineKeyboardButton(text=dialogs.RU_ru['help_cmd']['add_user_btn'],
                                        callback_data='add_user_help')
    white_list_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['white_list'],
                                          callback_data='white_list_2_help')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [white_list_btn],
        [add_user_btn]
    ])

    return keyboard


def create_help_menu_tokens_keyboard():
    tokens = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['token'], callback_data='tokens_2_help')
    add_token = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['add_token'], callback_data='add_token_help')
    back = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['back'], callback_data='help')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [tokens],
        [add_token],
        [back]
    ])

    return keyboard


def create_tokens_2_help_keyboard():
    facebook = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['facebook'], callback_data='tokens_help_facebook')
    other = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['other'], callback_data='tokens_help_other')
    youtube = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['youtube'], callback_data='tokens_help_youtube')
    back = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['back'], callback_data='tokens_help')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [facebook, youtube],
        [other],
        [back]
    ])

    return keyboard


def create_scheduler_count_keyboard(count, data):
    temp_dir = os.path.abspath(f'../Bot/temp/')
    file_name = os.path.join(temp_dir, f'{data}_scheduler.json')
    try:
        with open(file_name, 'r') as file:
            try:
                file_data = json.load(file)
            except json.JSONDecodeError:
                file_data = []
    except FileNotFoundError:
        file_data = []

    builder = InlineKeyboardBuilder()
    buttons = []

    for i in range(count+1):
        if i == 0:
            pass
        else:
            button_text = str(i)
            for item in file_data:
                if f'{data}_scheduler_{i}' in item:
                    button_text = item[f'{data}_scheduler_{i}']
                    break

            buttons.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f'scheduler_{i}'
            ))


    builder.row(*buttons, width=2)

    done_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['done'], callback_data='done')
    back_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['back'], callback_data=f'scheduler1_back')
    add_btn = InlineKeyboardButton(text='➕', callback_data=f'{data}_add')
    del_btn = InlineKeyboardButton(text='➖', callback_data=f'{data}_del')

    last_btns = InlineKeyboardMarkup(inline_keyboard=[
        [done_btn],
        [add_btn, del_btn],
        [back_btn]
    ])

    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))

    return builder.as_markup()


def create_fast_report_which_keyboard():
    facebook_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['facebook'], callback_data='fast_report_facebook')
    ewebinar_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['ewebinar'], callback_data='fast_report_ewebinar')
    getcourse_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['getcourse'], callback_data='fast_report_getcourse')
    all_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['all'], callback_data='fast_report_all')
    back_btn = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['menu'], callback_data='main_menu')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [facebook_btn],
        [ewebinar_btn],
        [getcourse_btn],
        [all_btn],
        [back_btn]
    ])

    return keyboard


def create_tokens_settings_keyboard(is_active):
    turn_on = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['activate'], callback_data='tokens_settings_activate')
    turn_off = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['deactivate'], callback_data='tokens_settings_deactivate')
    time = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['date_preset'], callback_data='tokens_settings_time')
    delete = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['delete'], callback_data='tokens_settings_delete')
    back = InlineKeyboardButton(text=dialogs.RU_ru['navigation']['back'], callback_data='tokens')

    if str(is_active).lower() == 'true':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [turn_off],
            # [time],
            [delete],
            [back]
        ])
        return keyboard
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [turn_on],
            # [time],
            [delete],
            [back]
        ])
        return keyboard

