from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.auth.schemas import UserRead
from app.schemas import PeriodFilters


class EvaluationsFilters(PeriodFilters):
    task_id: Annotated[int | None, Field(ge=1)] = None


class EvaluationBase(BaseModel):
    value: Annotated[int, Field(ge=1, le=5)]


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationRead(EvaluationBase):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(ge=1)]
    created_at: datetime

    author: UserRead
    task_id: Annotated[int, Field(ge=1)]


class EvaluationUpdate(BaseModel):
    value: Annotated[int | None, Field(ge=1, le=5)] = None
