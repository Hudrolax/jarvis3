from typing import TypedDict

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from api.auth import jwt_token
from dependencies import crypto_hash_factory
from domain.interfaces.user_ifaces import IUserRepoProtocol
from domain.models.user import User
from domain.services.user_service import IUserService, UserService
from infrastructure.db.models.user_orm import UserORM
from infrastructure.repositories.user_repo import UserRepo


def make_token(user: User) -> str:
    if not user.hashed_password:
        raise ValueError("Can't make a token for user without password.")
    token = jwt_token.create(user.username, user.hashed_password)
    return token


class UserToken(TypedDict):
    token: str
    user: User


# ********************* User utils *********************
def user_repo_factory(session: AsyncSession) -> IUserRepoProtocol:
    return UserRepo(session, domain_model=User, orm_class=UserORM)


def user_service_factory(session: AsyncSession) -> IUserService:
    repo = user_repo_factory(session)
    return UserService(repository=repo, crypto_hash=crypto_hash_factory())


async def make_user(
    session: AsyncSession,
    user: User,
    username: str = "john_doe",
    password: str = "password",
    telegram_id: int = 0,
    level: int = 0,
) -> User:
    service = user_service_factory(session)
    user = await service.create(
        user=user,
        username=username,
        password=password,
        telegram_id=telegram_id,
        level=level,
    )
    return user
