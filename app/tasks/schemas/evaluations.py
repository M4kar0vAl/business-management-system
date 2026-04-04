from datetime import date, datetime
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.auth.schemas import UserRead


def is_date_not_in_future(value: date | None) -> date:
    if value is not None and value > date.today():
        raise ValueError(f"{value} is in future")  # noqa: TRY003

    return value


class EvaluationsFilters(BaseModel):
    start: Annotated[date | None, AfterValidator(is_date_not_in_future)] = None
    end: date | None = None
    task_id: Annotated[int | None, Field(ge=1)] = None

    @model_validator(mode="after")
    def check_period(self) -> Self:
        if self.start and self.end and self.start > self.end:
            raise ValueError("Period 'start' cannot be later than 'end'")  # noqa: TRY003

        return self


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
