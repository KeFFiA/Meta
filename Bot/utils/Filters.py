from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import Message

from Database.database_query import admins_lists


class IsAdmin(BaseFilter):
    def __init__(self) -> None:
        self.user_ids = []

    async def __call__(self, message: Message) -> bool:
        self.user_ids = admins_lists()
        if isinstance(self.user_ids, int):
            print(True, 'is')
            return message.from_user.id != self.user_ids
        return message.from_user.id not in self.user_ids
