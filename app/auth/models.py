from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import ForeignKey, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.types import UserIdType
from app.mixins import IdIntPkMixin
from app.models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(IdIntPkMixin, SQLAlchemyBaseUserTable[UserIdType], Base):
    __tablename__ = "users"

    is_manager: Mapped[bool] = mapped_column(default=False, server_default=false())

    access_tokens: Mapped[list[AccessToken]] = relationship(back_populates="user")

    @classmethod
    def get_db(cls, session: AsyncSession) -> SQLAlchemyUserDatabase:
        return SQLAlchemyUserDatabase(session, cls)

    def __str__(self):
        return f"User <{self.email}>"


class AccessToken(SQLAlchemyBaseAccessTokenTable[UserIdType], Base):
    __tablename__ = "access_tokens"

    user_id: Mapped[UserIdType] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="access_tokens")

    @classmethod
    def get_db(cls, session: AsyncSession) -> SQLAlchemyAccessTokenDatabase:
        return SQLAlchemyAccessTokenDatabase(session, cls)

    def __str__(self):
        return f"AccessToken <{self.token}>"
