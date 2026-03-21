from typing import Annotated

from fastapi import Depends
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy

from app.auth.models import AccessToken
from app.config import settings

from .auth import get_access_token_db


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
):
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.AUTHENTICATION.ACCESS_TOKEN_LIFETIME_SECONDS,
    )
