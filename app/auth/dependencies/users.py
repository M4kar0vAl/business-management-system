from typing import Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.user_manager import UserManager
from app.dependencies import get_session


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield User.get_db(session)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)
