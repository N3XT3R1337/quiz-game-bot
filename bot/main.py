import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database import init_db
from bot.handlers import start_router, game_router, leaderboard_router


async def on_startup(bot: Bot):
    await init_db()
    logging.info("Database initialized")
    me = await bot.get_me()
    logging.info("Bot started: @%s", me.username)


async def on_shutdown(bot: Bot):
    logging.info("Bot shutting down...")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start_router)
    dp.include_router(game_router)
    dp.include_router(leaderboard_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
