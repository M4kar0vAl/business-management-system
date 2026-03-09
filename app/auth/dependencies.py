from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from fastapi_users.authentication.strategy.db import DatabaseStrategy

from app.auth.models import AccessToken, User
from app.auth.user_manager import UserManager
from app.config import settings
from app.dependencies import get_session

if TYPE_CHECKING:
    from fastapi_users.authentication.strategy.db import AccessTokenDatabase
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
    from sqlalchemy.ext.asyncio import AsyncSession


def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield User.get_db(session)


def get_access_token_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield AccessToken.get_db(session)


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
):
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.AUTHENTICATION.ACCESS_TOKEN_LIFETIME_SECONDS,
    )


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)
