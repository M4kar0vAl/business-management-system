from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User


async def list_users(session: AsyncSession) -> list[User]:
    """
    Get all users.

    :param session: sqlalchemy session
    :return: list of users
    """
    return list(await session.scalars(select(User)))
