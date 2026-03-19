import contextlib
import logging

from fastapi_users.exceptions import UserAlreadyExists

from app.auth.dependencies import get_user_db, get_user_manager
from app.auth.schemas import UserCreate
from app.dependencies import get_session

get_async_session_context = contextlib.asynccontextmanager(get_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


log = logging.getLogger(__file__)


async def create_user(email: str, password: str, is_superuser: bool = False):
    try:
        async with (
            get_async_session_context() as session,
            get_user_db_context(session) as user_db,
            get_user_manager_context(user_db) as user_manager,
        ):
            user = await user_manager.create(
                UserCreate(email=email, password=password, is_superuser=is_superuser)
            )
            log.info("User created %r", user)
            return user
    except UserAlreadyExists:
        log.warning("User %s already exists", email)
        raise
