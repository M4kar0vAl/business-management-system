from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import URL, MetaData, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


async def create_database(engine: AsyncEngine, db_name: str) -> None:
    """
    Create a new database if it does not exist.

    :param engine: db engine to connect to
    :param db_name: name of a database to create
    :return: None
    """
    async with engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))


async def drop_database(engine: AsyncEngine, db_name: str) -> None:
    """
    Drop a database if it exists.

    :param engine: db engine to connect to
    :param db_name: name of a database to drop
    :return: None
    """
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))


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
async def ensure_test_db(engine: AsyncEngine, db_name: str):
    """
    Context manager that ensures a test database exists.

    :param engine: db engine used to create a test database
    :param db_name: name of a test database to create
    :return: None
    """
    await create_database(engine, db_name)
    try:
        yield
    finally:
        await drop_database(engine, db_name)


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
