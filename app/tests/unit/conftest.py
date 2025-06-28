from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from domain.models.user import User

Base = declarative_base()

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# Фикстура для асинхронного движка с использованием StaticPool для in-memory SQLite
@pytest.fixture(scope="module")
async def async_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


# Фикстура для асинхронной сессии
@pytest.fixture
async def async_session(async_engine):
    async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session_factory() as session:  # type: ignore
        yield session


@pytest.fixture
def crypto_hash():
    mock = Mock()
    mock.verify = Mock(return_value=True)
    mock.hash = Mock(return_value="hashed_password")
    return mock


@pytest.fixture
def sample_user():
    return User(
        id=1,
        username="test",
        hashed_password="hashed_password",
        telegram_id=0,
        level=0,
    )


@pytest.fixture
def repo(sample_user: User):
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=sample_user)
    repo.create = AsyncMock(return_value=sample_user)
    repo.exists = AsyncMock(return_value=False)
    return repo
