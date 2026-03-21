from contextlib import asynccontextmanager

from app.database import Session


class UnitOfWork:
    def __init__(self):
        self.session = Session()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()

    async def flush(self):
        await self.session.flush()


@asynccontextmanager
async def unit_of_work():
    uow = UnitOfWork()
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
