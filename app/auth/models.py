from enum import StrEnum
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.types import UserIdType
from app.meetings.models import meeting_participants
from app.mixins import IdIntPkMixin
from app.models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.meetings.models import Meeting
    from app.tasks.models import Comment, Evaluation, Task
    from app.teams.models import Team


class Role(StrEnum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class User(IdIntPkMixin, SQLAlchemyBaseUserTable[UserIdType], Base):
    __tablename__ = "users"

    role: Mapped[Role] = mapped_column(default=Role.USER, server_default=Role.USER.name)
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id", ondelete="set null"), default=None
    )

    access_tokens: Mapped[list[AccessToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    team: Mapped[Team | None] = relationship(back_populates="users")
    tasks_authored: Mapped[list[Task]] = relationship(
        back_populates="author", foreign_keys="[Task.author_id]"
    )
    tasks_assigned: Mapped[list[Task]] = relationship(
        back_populates="assignee", foreign_keys="[Task.assignee_id]"
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    evaluations_as_author: Mapped[list[Evaluation]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    created_meetings: Mapped[list[Meeting]] = relationship(
        back_populates="created_by",
        foreign_keys="[Meeting.created_by_id]",
        cascade="all, delete-orphan",
    )
    meetings: Mapped[list[Meeting]] = relationship(
        back_populates="participants",
        secondary=meeting_participants,
        passive_deletes=True,
    )

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
