from datetime import datetime

from pydantic import BaseModel

from app.auth.schemas import UserRead


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
