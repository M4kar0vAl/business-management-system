from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.tasks.models import TaskStatus


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


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

    team_id: Annotated[int, Field(ge=1)]
    author_id: Annotated[int | None, Field(ge=1)]
    assignee_id: Annotated[int | None, Field(ge=1)]


class TaskUpdate(BaseModel):
    description: str | None = None
    deadline: datetime | None = None
    status: TaskStatus | None = None
