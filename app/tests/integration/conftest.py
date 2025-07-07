from typing import Any, AsyncGenerator

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from domain.models.user import User
from infrastructure.db.db import Base, get_db
from main import app as actual_app

from .test_utils import UserToken, make_token, make_user

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# Создаем асинхронный движок; каждый тест получает новый движок
@pytest.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False, "uri": True},
        poolclass=StaticPool,
    )
    yield engine
    await engine.dispose()


# Фикстура, которая открывает соединение на время теста.
@pytest.fixture(scope="function")
async def async_connection(async_engine) -> AsyncGenerator[AsyncConnection, None]:
    connection = await async_engine.connect()
    yield connection
    await connection.close()


# Синхронная функция для применения миграций на данном соединении.
def run_migrations_sync(connection):
    # Загружаем конфигурацию Alembic
    cfg = Config("alembic.ini")
    # Переопределяем URL, чтобы использовать нашу in‑memory базу
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    script = ScriptDirectory.from_config(cfg)

    # Функция-обертка для выполнения апгрейда до "head"
    def upgrade(rev, context):
        return script._upgrade_revs("head", rev)

    # Здесь мы используем MigrationContext.configure, передавая целевую metadata и функцию upgrade
    migration_ctx = MigrationContext.configure(connection, opts={"target_metadata": Base.metadata, "fn": upgrade})
    # В рамках транзакции запускаем миграции
    with connection.begin():
        with Operations.context(migration_ctx):
            migration_ctx.run_migrations()


# Фикстура, которая применяет миграции для каждого теста, используя то же соединение.
@pytest.fixture(scope="function")
async def apply_alembic_migrations(async_connection):
    await async_connection.run_sync(run_migrations_sync)
    yield


# Фикстура, создающая асинхронную сессию, привязанную к тому же соединению с применёнными миграциями.
@pytest.fixture(scope="function")
async def session(async_connection, apply_alembic_migrations):
    async_session_factory = async_sessionmaker(bind=async_connection, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, session) -> None:
    """Overriding session generator in the app"""

    async def get_db_session_override():
        """Generator with test session"""
        yield session

    app.dependency_overrides[get_db] = get_db_session_override


@pytest.fixture
async def app():
    async with LifespanManager(actual_app):
        yield actual_app


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, Any]:
    # Теперь внутри уже отработавшего startup
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def new_user(session: AsyncSession) -> User:
    superuser = User(
        id=999,
        username="super",
        hashed_password="xxx",
        telegram_id=0,
        level=0,
    )
    return await make_user(session, superuser)


async def user_token_generator(session: AsyncSession, level: int = 0) -> AsyncGenerator[UserToken, None]:
    payload = {"username": "Authorized user", "password": "password", "telegram_id": 0, "level": level}
    super = User(
        id=999,
        username="super",
        hashed_password="xxx",
        telegram_id=99,
        level=99,
    )
    user = await make_user(session=session, user=super, **payload)
    token = make_token(user)
    yield UserToken(token=token, user=user)


@pytest.fixture
async def user_token(session: AsyncSession) -> AsyncGenerator[UserToken, None]:
    user_token = user_token_generator(session)
    yield await user_token.__anext__()


@pytest.fixture
async def super_user_token(session: AsyncSession) -> AsyncGenerator[UserToken, None]:
    user_token = user_token_generator(session, level=99)
    yield await user_token.__anext__()
