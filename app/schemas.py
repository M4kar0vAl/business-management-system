from datetime import date
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, field_validator, model_validator


class BaseResponse(BaseModel):
    detail: str


class ErrorResponse(BaseResponse):
    pass


class SuccessResponse(BaseResponse):
    pass


def is_date_not_in_future(value: date | None) -> date:
    if value is not None and value > date.today():
        raise ValueError(f"{value} is in future")  # noqa: TRY003

    return value


class PeriodFilters(BaseModel):
    start: Annotated[date | None, AfterValidator(is_date_not_in_future)] = None
    end: date | None = None

    @model_validator(mode="after")
    def check_period(self) -> Self:
        if self.start and self.end and self.start > self.end:
            raise ValueError("Period 'start' cannot be later than 'end'")  # noqa: TRY003

        return self

    @field_validator("start", "end", mode="before")
    @classmethod
    def empty_date_strings_to_none(cls, v):
        if v == "":
            return None
        return v
