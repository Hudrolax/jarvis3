import asyncio
import logging

from domain.util import stop_event
from telegram.bot_factory import create_bots

logger = logging.getLogger(__name__)

async def run_bots():
    bots = create_bots()
    tasks: list[asyncio.Task] = []

    for bot, dp in bots:
        async def _start(bot=bot, dp=dp):
            while True:
                try:
                    logger.info("Start polling %s", bot.token[-6:])
                    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
                except Exception as e:
                    logger.error("Polling error for %s: %r — перезапускаю через 5 секунд", bot.token[-6:], e)
                    await asyncio.sleep(5)
                else:
                    # если start_polling отработал без ошибок (например, его кто-то остановил), то тоже выходим из цикла
                    break
        tasks.append(asyncio.create_task(_start()))

    stop_task = asyncio.create_task(stop_event.wait())
    await stop_task

    # корректный останов
    for t in tasks:
        t.cancel()
