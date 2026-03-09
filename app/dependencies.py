from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Session

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from typing import Any


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with Session() as session:
        yield session
