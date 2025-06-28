from abc import ABC, abstractmethod


class IMessageRouter(ABC):
    @abstractmethod
    async def append(self, data: LinkDict) -> Link: ...

    @abstractmethod
    async def find(self, user: User, request: str) -> list[Link]: ...

    @abstractmethod
    async def update(self, user: User, id: int, data: LinkDict) -> Link: ...

    @abstractmethod
    async def remove(self, user: User, id: int) -> bool: ...


