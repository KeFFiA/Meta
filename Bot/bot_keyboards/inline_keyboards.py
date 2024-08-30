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
    last_btns = InlineKeyboardMarkup(inline_keyboard=[[last_btn_2, last_btn_1]])
    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))
    return builder.as_markup()


def create_token_list_keyboard():
    builder = InlineKeyboardBuilder()
    button = token_list()
    buttons = []
    for data, text in button.items():
        try:
            buttons.append(InlineKeyboardButton(
                text=f"[{text['service']}]  "+text['token'][:25],
                callback_data=data
            ))
        except:
            pass

    builder.row(*buttons, width=1)
    last_btn_1 = InlineKeyboardButton(callback_data='next_page', text='-->')
    last_btn_2 = InlineKeyboardButton(callback_data='last_page', text='<--')
    last_btns = InlineKeyboardMarkup(inline_keyboard=[[last_btn_2, last_btn_1]])
    # builder.attach(InlineKeyboardBuilder.from_markup(last_btns))
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

    last_btns = InlineKeyboardMarkup(inline_keyboard=[
        [preset_btn, level_btn, increment_btn],
        [activate_all_btn, back_btn, deactivate_all_btn]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(last_btns))

    return builder.as_markup()








