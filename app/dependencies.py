# app/deps.py
import sys
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from domain.interfaces import (
    IEmbeddingClient,
    IEmbeddingService,
    ILinkRepoProtocol,
    ILinkService,
    IUserRepoProtocol,
    IUserService,
)
from domain.models import Link, User
from domain.services import EmbeddingService, LinkService, UserService
from infrastructure.clients import OpenAIEmbeddingClient
from infrastructure.db.db import get_db
from infrastructure.db.models import LinkORM, UserORM
from infrastructure.deps_injector import Depends, service_injector
from infrastructure.repositories import LinkRepo, UserRepo
from utils.crypto_hash import AbstractCrypto, Argon2Crypto


def fastapi_inject(domain_fn):
    async def _inject():
        # 1. создаём сервис и всё что ему нужно
        service, async_gens, sync_ctxs = await service_injector(domain_fn)(return_ctx=True)

        try:
            yield service          # отдаём объект маршруту
        finally:
            # 2. закрываем всё то, что service_injector положил в списки
            for agen in reversed(async_gens):
                try:
                    await agen.__anext__()
                except StopAsyncIteration:
                    pass
            for cm in reversed(sync_ctxs):
                cm.__exit__(*sys.exc_info())
    return _inject


def crypto_hash_factory() -> AbstractCrypto:
    return Argon2Crypto()


# ****** User dependencies ******
def user_repo_factory(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IUserRepoProtocol:
    return UserRepo(db, domain_model=User, orm_class=UserORM)


def get_user_service(repo: Annotated[IUserRepoProtocol, Depends(user_repo_factory)]) -> IUserService:
    return UserService(repository=repo, crypto_hash=crypto_hash_factory())


# ****** Link dependencies ******
def link_repo_factory(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ILinkRepoProtocol:
    return LinkRepo(db, domain_model=Link, orm_class=LinkORM)


def embedding_client_factory() -> IEmbeddingClient:
    return OpenAIEmbeddingClient(api_key=settings.OPENAI_API_KEY)


def get_link_service(
    repo: Annotated[ILinkRepoProtocol, Depends(link_repo_factory)],
    embedding_client: Annotated[IEmbeddingService, Depends(embedding_client_factory)],
) -> ILinkService:
    return LinkService(repository=repo, embed_service=EmbeddingService(client=embedding_client))

