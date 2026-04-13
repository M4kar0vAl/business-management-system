from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.auth.schemas import UserRead
from app.schemas import CalendarFilters, PeriodFilters


class MeetingFilters(PeriodFilters):
    pass


class MeetingBase(BaseModel):
    start_time: datetime
    end_time: datetime


class MeetingCreate(MeetingBase):
    pass


class MeetingRead(MeetingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: UserRead


class MeetingReadFull(MeetingRead):
    participants: list[UserRead]


class MeetingsCalendarFilters(CalendarFilters):
    user_id: int | None = None
