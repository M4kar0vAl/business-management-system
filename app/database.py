from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.DB.URL)

Session = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)
