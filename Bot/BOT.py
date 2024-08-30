import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from Bot.Handlers.admin_handlers import admin_router
from Bot.Handlers.user_handlers import user_router
from logging_settings import bot_logger

from Bot.utils.middlewares import CheckInWhiteListMiddleware, CheckInAdminListMiddleware


async def main():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"), timeout=120)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(admin_router)
    dp.include_router(user_router)

    admin_router.message.middleware(CheckInAdminListMiddleware())
    admin_router.callback_query.middleware(CheckInAdminListMiddleware())
    dp.update.outer_middleware(CheckInWhiteListMiddleware())
    dp.message.middleware(ChatActionMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    bot_logger.info(msg=Bot)


if __name__ == "__main__":
    asyncio.run(main())
