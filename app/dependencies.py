from typing import TYPE_CHECKING, Annotated

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Session
from app.uow import UnitOfWork, unit_of_work

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from typing import Any


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with Session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_uow(
    session: SessionDep,
) -> AsyncGenerator[UnitOfWork, Any]:
    async with unit_of_work(session) as uow:
        yield uow


UOWDep = Annotated[UnitOfWork, Depends(get_uow)]


async def get_async_client() -> AsyncGenerator[httpx.AsyncClient, Any]:
    async with httpx.AsyncClient() as client:
        yield client


AsyncClientDep = Annotated[httpx.AsyncClient, Depends(get_async_client)]
