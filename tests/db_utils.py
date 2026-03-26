from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from asyncpg import InvalidCatalogNameError
from sqlalchemy import URL, MetaData, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


async def db_exists(db_url: str | URL) -> bool:
    """
    Check if db with the given url exists

    :param db_url: db url as a string
    :return: boolean indicating whether db exists or not
    """
    engine = create_async_engine(db_url)

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except OperationalError, ProgrammingError, InvalidCatalogNameError:
        return False
    else:
        return True
    finally:
        await engine.dispose()


async def create_database(engine: AsyncEngine, db_url: URL) -> None:
    """
    Create a new database if it does not exist.

    :param engine: db engine to connect to
    :param db_url: url of a database to create
    :return: None
    """
    if not await db_exists(db_url):
        async with engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE {db_url.database}"))


async def drop_database(engine: AsyncEngine, db_url: URL) -> None:
    """
    Drop a database if it exists.

    :param engine: db engine to connect to
    :param db_url: url of a database to drop
    :return: None
    """
    if await db_exists(db_url):
        async with engine.connect() as conn:
            await conn.execute(text(f"DROP DATABASE {db_url.database}"))


@asynccontextmanager
async def async_db_engine(
    db_url: str | URL, **kwargs
) -> AsyncGenerator[AsyncEngine, Any]:
    """
    Context manager that creates a new async engine for a database.

    :param db_url: url of a database to create engine for
    :param kwargs: additional arguments to pass in engine creating function
    :return: AsyncEngine instance
    """
    db_engine_obj = create_async_engine(db_url, **kwargs)
    try:
        yield db_engine_obj
    finally:
        await db_engine_obj.dispose()


@asynccontextmanager
async def ensure_test_db(engine: AsyncEngine, db_url: URL):
    """
    Context manager that ensures a test database exists.

    :param engine: db engine used to create a test database
    :param db_url: url of a test database to create
    :return: None
    """
    await create_database(engine, db_url)
    try:
        yield
    finally:
        await drop_database(engine, db_url)


@asynccontextmanager
async def ensure_db_schema(engine: AsyncEngine, metadata: MetaData):
    """
    Context manager that ensures a database schema exists.

    :param engine: db engine used to apply database schema
    :param metadata: MetaData object containing info about the database schema
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
