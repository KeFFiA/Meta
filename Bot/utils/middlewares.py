from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, TelegramObject

from Bot import dialogs
from Database.database import db


class CheckInWhiteListMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.white_users = []

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        user_id = data["event_from_user"].id
        users = db.query(query="SELECT user_id FROM white_list", fetch='fetchall')
        self.white_users = [item for tup in users for item in tup]
        if user_id in self.white_users:
            return await handler(event, data)
        else:
            return await event.message.answer(
                dialogs.RU_ru['/start_unsuccessful'] +
                f'\n\n<i>Ваш ID: <code>{user_id}</code></i>',
                parse_mode='HTML'
            )


class CheckInAdminListMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.admin_users = []

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        user_id = data["event_from_user"].id
        users = db.query(query="SELECT user_id FROM white_list WHERE admin=true", fetch='fetchall')
        self.admin_users = [item for tup in users for item in tup]
        if user_id in self.admin_users:
            return await handler(event, data)
        else:
            return await event.answer(
                dialogs.RU_ru['not_admin'] +
                f'\n\n<i>Ваш ID: <code>{user_id}</code></i>',
                parse_mode='HTML'
            )
