from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, List, Tuple

from ..models.message import Message

FilterFn = Callable[[Message], bool]
Handler = Callable[[Message], Awaitable[Any]]

class IMessageRouter(ABC):
    _routes: List[Tuple[FilterFn, Handler]] = []

    @abstractmethod
    def message(self, filter_fn: FilterFn = lambda _: True) -> Callable: ...


