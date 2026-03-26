import logging

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.auth.models import User
from app.auth.schemas import UserCreate
from app.auth.user_manager import UserManager
from app.config import DatabaseConfig, Settings
from app.config import settings as app_settings
from app.dependencies import get_session
from app.main import app
from app.models import Base
from tests.db_utils import (
    async_db_engine,
    drop_database,
    ensure_db_schema,
    ensure_test_db,
)


@pytest.fixture(scope="session", autouse=True)
def disable_logging():
    """Disable logging in tests"""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture(scope="session")
async def settings() -> Settings:
    app_db_settings = app_settings.DB
    db_conf = DatabaseConfig(
        USER=app_db_settings.USER,
        PASS=app_db_settings.PASS.get_secret_value(),
        HOST=app_db_settings.HOST,
        PORT=app_db_settings.PORT,
        NAME=f"test_{app_db_settings.NAME}",
    )

    return Settings(DB=db_conf)


@pytest.fixture(scope="session")
async def engine(settings):
    db_settings = settings.DB
    admin_db_url = URL.create(
        drivername="postgresql+asyncpg",
        database="postgres",
        host=db_settings.HOST,
        port=db_settings.PORT,
        username=db_settings.USER,
        password=db_settings.PASS.get_secret_value(),
    )

    async with async_db_engine(
        admin_db_url, isolation_level="AUTOCOMMIT"
    ) as admin_engine:
        # drop db if it remained after previous tests
        await drop_database(admin_engine, db_settings.URL)

        async with (
            ensure_test_db(admin_engine, db_settings.URL),  # create test db
            async_db_engine(
                db_settings.URL,
                poolclass=NullPool,
            ) as async_engine,  # create engine connected to tst db
            ensure_db_schema(async_engine, Base.metadata),  # create tables
        ):
            yield async_engine


@pytest.fixture
async def session(engine):
    async with engine.connect() as conn:
        trans = await conn.begin()

        Session = async_sessionmaker(
            bind=conn,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with Session() as session:
            yield session

        await trans.rollback()


@pytest.fixture
async def async_client(session):
    async def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def user_db(session):
    return User.get_db(session)


@pytest.fixture
async def user_manager(user_db):
    return UserManager(user_db)


@pytest.fixture
async def create_user(user_manager, authenticate_user):

    async def _create_user(user: UserCreate, authenticate: bool = False):
        db_user = await user_manager.create(user)
        token = None

        if authenticate:
            db_user, token = await authenticate_user(user.email, user.password)

        return db_user, token

    return _create_user
