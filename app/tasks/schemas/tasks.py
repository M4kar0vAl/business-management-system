from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.auth.schemas import UserRead
from app.tasks.models import TaskStatus
from app.tasks.schemas import CommentRead
from app.teams.schemas import TeamRead


class TaskBase(BaseModel):
    description: str
    deadline: datetime
    status: TaskStatus = TaskStatus.OPEN


class TaskCreate(TaskBase):
    @field_validator("deadline", mode="after")
    @classmethod
    def validate_deadline(cls, deadline: datetime):
        if deadline <= datetime.now():
            raise ValueError("Deadline must be in the future")  # noqa: TRY003

        return deadline


class TaskReadBase(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class TaskRead(TaskReadBase):
    team_id: Annotated[int, Field(ge=1)]
    author_id: Annotated[int | None, Field(ge=1)]
    assignee_id: Annotated[int | None, Field(ge=1)]


class TaskReadFull(TaskReadBase):
    team: TeamRead
    author: UserRead
    assignee: UserRead
    comments: list[CommentRead]


class TaskUpdate(BaseModel):
    description: str | None = None
    deadline: datetime | None = None
    status: TaskStatus | None = None
