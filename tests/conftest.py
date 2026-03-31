import logging

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from httpx import ASGITransport, AsyncClient
from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.auth.backend import authentication_backend
from app.auth.models import AccessToken, User
from app.auth.schemas import UserCreate
from app.auth.user_manager import UserManager
from app.config import DatabaseConfig, Settings
from app.config import settings as app_settings
from app.dependencies import get_session
from app.main import app
from app.models import Base
from app.tasks.models import Task
from app.tasks.repositories import TaskRepository
from app.tasks.schemas import TaskCreate
from app.tasks.services import TaskService
from app.teams.repositories import TeamRepository
from app.teams.schemas import TeamCreate
from app.teams.services import TeamService
from app.uow import unit_of_work
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
async def uow(session):
    async with unit_of_work(session) as _uow:
        yield _uow


@pytest.fixture
async def user_db(session):
    return User.get_db(session)


@pytest.fixture
async def access_token_db(session):
    return AccessToken.get_db(session)


@pytest.fixture
async def user_manager(user_db):
    return UserManager(user_db)


@pytest.fixture
async def authenticate_user(access_token_db, user_manager):
    async def _authenticate_user(email, password):
        user = await user_manager.authenticate(
            OAuth2PasswordRequestForm(username=email, password=password)
        )

        assert user is not None, f"Could not authenticate user {email}"

        strategy = authentication_backend.get_strategy(access_token_db)
        token = await strategy.write_token(user)

        return user, token

    return _authenticate_user


@pytest.fixture
async def create_user(user_manager, authenticate_user):

    async def _create_user(user: UserCreate, authenticate: bool = False):
        db_user = await user_manager.create(user)
        token = None

        if authenticate:
            db_user, token = await authenticate_user(user.email, user.password)

        return db_user, token

    return _create_user


@pytest.fixture(scope="session")
def get_authorization_header():

    def _get_authorization_header(token):
        return {
            "Authorization": f"Bearer {token}",
        }

    return _get_authorization_header


@pytest.fixture
async def team_repository(session):
    return TeamRepository(session)


@pytest.fixture
async def team_service(uow, user_manager):
    return TeamService(uow, user_manager)


@pytest.fixture
async def create_team(team_service, team_repository):

    async def _create_team(team_create: TeamCreate, members: list[User] | None = None):
        team = await team_service.create_team(team_create)
        members = members or []

        for member in members:
            await team_repository.assign_user_to_team(team, member)

        await team_service.uow.flush()
        return team

    return _create_team


@pytest.fixture
async def task_repository(session):
    return TaskRepository(session)


@pytest.fixture
async def task_service(uow, user_manager):
    return TaskService(uow, user_manager)


@pytest.fixture
async def create_task(task_service):

    async def _create_task(
        task: TaskCreate, author: User, assignee: User | None = None
    ) -> Task:
        created_task = await task_service.create_task(task, author)

        if assignee:
            created_task.assignee_id = assignee.id

        await task_service.uow.flush()
        return created_task

    return _create_task
