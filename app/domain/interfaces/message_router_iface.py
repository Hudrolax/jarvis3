from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, List, Tuple

from ..models.message import Message

FilterFn = Callable[[Message], bool]
Handler = Callable[..., Awaitable[Any]]

class IMessageRouter(ABC):
    _routes: List[Tuple[FilterFn, Handler]] = []
    _routers: List['IMessageRouter'] = []

    @abstractmethod
    def message(self, filter_fn: FilterFn = lambda _: True) -> Callable: ...

    @abstractmethod
    def include_router(self, router: 'IMessageRouter') -> None: ...

    @abstractmethod
    def include_middleware(self, router: 'IMessageRouter') -> None: ...

    @abstractmethod
    async def dispatch(self, dm: Message):
        """
        Пробегаемся по всем зарегистрированным маршрутам
        и вызываем те, чей фильтр вернул True.
        """
        ...
