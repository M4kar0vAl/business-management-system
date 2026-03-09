from enum import StrEnum
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.types import UserIdType
from app.mixins import IdIntPkMixin
from app.models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Role(StrEnum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class User(SQLAlchemyBaseUserTable[UserIdType], IdIntPkMixin, Base):
    __tablename__ = "users"

    role: Mapped[Role] = mapped_column(default=Role.USER, server_default=Role.USER.name)

    @classmethod
    def get_db(cls, session: AsyncSession) -> SQLAlchemyUserDatabase:
        return SQLAlchemyUserDatabase(session, cls)
