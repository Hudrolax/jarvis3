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
            logger.info("Start polling %s", bot.token[-6:])
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        tasks.append(asyncio.create_task(_start()))

    # ждём глобального stop_event (при shutdown FastAPI) или падения тасок
    await asyncio.wait([asyncio.create_task(stop_event.wait()), *tasks], return_when=asyncio.FIRST_COMPLETED)

    # корректный останов
    for t in tasks:
        t.cancel()
