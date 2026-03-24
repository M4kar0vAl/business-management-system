from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=settings.DB.NAMING_CONVENTION)
