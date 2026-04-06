from datetime import datetime

from pydantic import BaseModel

from app.auth.schemas import UserRead
from app.schemas import PeriodFilters


class MeetingFilters(PeriodFilters):
    pass


class MeetingBase(BaseModel):
    start_time: datetime
    end_time: datetime


class MeetingCreate(MeetingBase):
    pass


class MeetingRead(MeetingBase):
    id: int
    created_by: UserRead


class MeetingReadFull(MeetingRead):
    participants: list[UserRead]
