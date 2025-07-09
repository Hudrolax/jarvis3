import logging
from typing import List, Tuple

from domain.interfaces.message_router_iface import FilterFn, Handler, IMessageRouter
from domain.models.message import Message

from .injector import service_injector

logger = logging.getLogger(__name__)


class DomainMessageRouter(IMessageRouter):
    def __init__(self) -> None:
        self._routes: List[Tuple[FilterFn, Handler]] = []
        self._routers: List['IMessageRouter'] = []
        self._middlewares: List['IMessageRouter'] = []
        logger.debug('Init domain message router.')

    def include_router(self, router: 'IMessageRouter') -> None:
        self._routers.append(router)

    def include_middleware(self, router: 'IMessageRouter') -> None:
        self._routers.append(router)

    def message(self, filter_fn: FilterFn = lambda _: True):
        """
        Декоратор: @domain_router.message(lambda m: m.text == "/start")
        """
        def decorator(fn: Handler) -> Handler:
            wrapped = service_injector(fn)
            self._routes.append((filter_fn, wrapped))
            return wrapped
        return decorator

    async def dispatch(self, dm: Message):
        """
        Пробегаемся по всем зарегистрированным маршрутам
        и вызываем те, чей фильтр вернул True.
        """
        try:
            # handle middlewares
            for router in self._middlewares:
                for filter_fn, handler in router._routes:
                    try:
                        if filter_fn(dm):
                            logger.debug(f'Handle message: {dm}')
                            await handler(dm)
                    except Exception as ex:
                        logger.error(ex)
                        raise

            # handle self routes
            for filter_fn, handler in self._routes:
                try:
                    if filter_fn(dm):
                        logger.debug(f'Handle message: {dm}')
                        await handler(dm)
                except Exception as ex:
                    logger.error(ex)
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
                        raise
        except Exception:
            await dm.answer(Message(text='Непредвиденная ошибка'))
            raise

