from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.database import Session
from app.uow import UnitOfWork, unit_of_work

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from typing import Any

    from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with Session() as session:
        yield session


async def get_uow(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[UnitOfWork, Any]:
    async with unit_of_work(session) as uow:
        yield uow


UOWDep = Annotated[UnitOfWork, Depends(get_uow)]
