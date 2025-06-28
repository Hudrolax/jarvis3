from pprint import pprint as print
from typing import Any, Awaitable, Callable, List, Tuple

from ..models.message import Message

FilterFn = Callable[[Message], bool]
Handler = Callable[[Message], Awaitable[Any]]

class DomainRouter:
    def __init__(self) -> None:
        self._routes: List[Tuple[FilterFn, Handler]] = []

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
        for filter_fn, handler in self._routes:
            try:
                if filter_fn(dm):
                    await handler(dm)
            except Exception:
                # тут можно залогировать ошибку
                raise

domain_router = DomainRouter()


@domain_router.message(lambda m: m.text == "hello")
async def domain_route(msg: Message):
    print(msg)
    await msg.answer(Message(text='HELLLOOOOOO'))


@domain_router.message(lambda m: m.text == "test")
async def echo_router(msg: Message):
    print(msg)
    await msg.answer(Message(text='Teeest'))
