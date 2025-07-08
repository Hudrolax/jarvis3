import logging
from typing import List, Tuple

from domain.interfaces.message_router_iface import FilterFn, Handler, IMessageRouter
from domain.models.message import Message

logger = logging.getLogger(__name__)


class DomainMessageRouter(IMessageRouter):
    def __init__(self) -> None:
        self._routes: List[Tuple[FilterFn, Handler]] = []
        self._routers: List['IMessageRouter'] = []
        logger.debug('Init domain message router.')

    def include_router(self, router: 'IMessageRouter') -> None:
        self._routers.append(router)

    def message(self, filter_fn: FilterFn = lambda _: True):
        """
        Декоратор: @domain_router.message(lambda m: m.text == "/start")
        """
        def decorator(fn: Handler) -> Handler:
            self._routes.append((filter_fn, fn))
            return fn
        return decorator

    async def dispatch(self, dm: Message):
        """
        Пробегаемся по всем зарегистрированным маршрутам
        и вызываем те, чей фильтр вернул True.
        """
        # handle self routes
        for filter_fn, handler in self._routes:
            try:
                if filter_fn(dm):
                    logger.debug(f'Handle message: {dm}')
                    await handler(dm)
            except Exception as ex:
                logger.error(ex)
                try:
                    await dm.answer(Message(text='Непредвиденная ошибка'))
                except Exception:
                    pass
                raise

        # handle include routers
        for router in self._routers:
            for filter_fn, handler in router._routes:
                try:
                    if filter_fn(dm):
                        logger.debug(f'Handle message: {dm}')
                        await handler(dm)
                except Exception as ex:
                    logger.error(ex)
                    try:
                        await dm.answer(Message(text='Непредвиденная ошибка'))
                    except Exception:
                        pass
                    raise

