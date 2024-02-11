import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config.config import config
from menu_commands import set_default_commands
from handlers import authorise, start_shift, check_attractions, finish_shift, encahment, adm_stats

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.token)
storage = RedisStorage(redis=config.redis)
dp = Dispatcher(storage=storage)


async def main() -> None:
    # Подключаем роутеры к диспетчеру
    dp.include_router(authorise.router_authorise)
    dp.include_router(start_shift.router_start_shift)
    dp.include_router(check_attractions.router_attractions)
    dp.include_router(encahment.router_encashment)
    dp.include_router(finish_shift.router_finish)
    dp.include_router(adm_stats.router_adm)

    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())