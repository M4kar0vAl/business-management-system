from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.types import UserIdType
from app.mixins import CreatedAtMixin, IdIntPkMixin
from app.models import Base

if TYPE_CHECKING:
    from app.auth.models import User
    from app.teams.models import Team


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(IdIntPkMixin, CreatedAtMixin, Base):
    __tablename__ = "tasks"

    description: Mapped[str]
    deadline: Mapped[datetime]
    status: Mapped[TaskStatus] = mapped_column(
        default=TaskStatus.OPEN, server_default=TaskStatus.OPEN.name
    )

    author_id: Mapped[UserIdType | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), default=None
    )
    assignee_id: Mapped[UserIdType | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), default=None
    )
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))

    author: Mapped[User | None] = relationship(back_populates="tasks_authored")
    assignee: Mapped[User | None] = relationship(back_populates="tasks_assigned")
    team: Mapped[Team] = relationship(back_populates="tasks")
    comments: Mapped[list[Comment]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class Comment(IdIntPkMixin, CreatedAtMixin, Base):
    __tablename__ = "comments"

    text: Mapped[str] = mapped_column(Text(), default="", server_default="")

    user_id: Mapped[UserIdType] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="comments")
    task: Mapped[Task] = relationship(back_populates="comments")
