from abc import ABC, abstractmethod
from typing import Protocol

from ..interfaces.mixins_repo_iface import (
    ICreate,
    IDelete,
    IExists,
    IList,
    IRead,
    IUpdate,
    IVectorSearch,
)
from ..models.base_domain_model import TDomain
from ..models.link import Link, LinkDict, LinkFields
from ..models.user import User


class ILinkRepoProtocol(
    ICreate[TDomain, LinkDict],
    IRead[TDomain, LinkDict],
    IUpdate[TDomain, LinkDict],
    IList[TDomain, LinkDict, LinkFields],
    IExists[LinkDict],
    IDelete[LinkDict],
    IVectorSearch[TDomain, LinkDict],
    Protocol,
): ...


class ILinkService(ABC):
    @abstractmethod
    async def append(self, data: LinkDict) -> Link: ...

    @abstractmethod
    async def find(self, user: User, request: str) -> list[Link]: ...

    @abstractmethod
    async def update(self, user: User, id: int, data: LinkDict) -> Link: ...

    @abstractmethod
    async def remove(self, user: User, id: int) -> bool: ...


class ILinkFilterAgent(Protocol):
    async def filter_links_by_prompt(self, links, prompt: str) -> list: ...
