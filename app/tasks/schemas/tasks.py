from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.auth.schemas import UserRead
from app.schemas import CalendarFilters
from app.tasks.models import TaskStatus


class TaskBase(BaseModel):
    description: str
    deadline: datetime
    status: TaskStatus = TaskStatus.OPEN


class TaskCreate(TaskBase):
    team_id: Annotated[int, Field(ge=1)]

    @field_validator("deadline", mode="after")
    @classmethod
    def validate_deadline(cls, deadline: datetime):
        if deadline <= datetime.now(UTC):
            raise ValueError("Deadline must be in the future")  # noqa: TRY003

        return deadline


class TaskReadBase(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    team_id: Annotated[int, Field(ge=1)]


class TaskRead(TaskReadBase):
    author_id: Annotated[int | None, Field(ge=1)]
    assignee_id: Annotated[int | None, Field(ge=1)]


class TaskReadFull(TaskReadBase):
    author: UserRead | None
    assignee: UserRead | None


class TaskUpdate(BaseModel):
    description: str | None = None
    deadline: datetime | None = None
    status: TaskStatus | None = None

    @field_validator("deadline", mode="after")
    @classmethod
    def validate_deadline(cls, deadline: datetime | None):
        if deadline is not None and deadline <= datetime.now(UTC):
            raise ValueError("Deadline must be in the future")  # noqa: TRY003

        return deadline


class TasksCalendarFilters(CalendarFilters):
    team_id: int | None = None
    assignee_id: int | None = None
