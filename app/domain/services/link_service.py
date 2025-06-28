import logging

from ..exceptions import NotFoundError
from ..interfaces.embedding_ifaces import IEmbeddingService
from ..interfaces.link_ifaces import ILinkRepoProtocol, ILinkService
from ..models.link import Link, LinkDict
from ..models.user import User

logger = logging.getLogger(__name__)


class LinkService(ILinkService):
    repository: ILinkRepoProtocol
    embed_service: IEmbeddingService

    def __init__(self, repository: ILinkRepoProtocol, embed_service: IEmbeddingService) -> None:
        self.repository = repository
        self.embed_service = embed_service

    async def append(self, data: LinkDict) -> Link:
        return await self.repository.create(data)

    async def find(self, user: User, request: str) -> list[Link]:
        request_embed = await self.embed_service.embed(request)
        db_links = await self.repository.list_by_embedding(request_embed, limit=10, filters={'user_id': user.id})
        if len(db_links) == 0:
            raise NotFoundError('Не найдено ссылок по вашему запросу.')

        links = db_links
        if len(links) == 0:
            raise NotFoundError('Не найдено ссылок по вашему запросу.')

        return links

    async def update(self, user: User, id: int, data: LinkDict) -> Link:
        updated_recors = await self.repository.update(data=data, filters={"id": id, "user_id": user.id})
        if updated_recors == 0:
            raise NotFoundError
        return updated_recors[0]

    async def remove(self, user: User, id: int) -> bool:
        deleted_count = await self.repository.delete(filters={'user_id': user.id, 'id': id})
        return bool(deleted_count)
