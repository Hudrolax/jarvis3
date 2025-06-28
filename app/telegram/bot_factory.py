from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from .adapter import apply_dispatcher_adapter
from .middlewares import InjectServicesMiddleware
from .settings import telegram_settings


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(InjectServicesMiddleware())
    apply_dispatcher_adapter(dp)

    return dp

def create_bots() -> list[tuple[Bot, Dispatcher]]:
    bots = []
    for cfg in telegram_settings.bots:
        session = AiohttpSession(proxy=telegram_settings.proxy)
        bot = Bot(cfg.token, session=session)
        bots.append((bot, build_dispatcher()))
    return bots
