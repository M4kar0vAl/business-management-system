from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.auth.models import User


class OverlappingMeetingError(Exception):
    """
    Raised when the meeting time overlaps with another meeting
    """

    def __init__(self, start_time: datetime, end_time: datetime):
        self.start_time = start_time
        self.end_time = end_time
        self.message = f"Meeting with interval [{self.start_time} - {self.end_time}] overlaps with another one"
        super().__init__(self.message)


class MeetingDoesNotExistError(Exception):
    """
    Raised when the meeting does not exist
    """

    def __init__(self, meeting_id):
        self.meeting_id = meeting_id
        self.message = f"Meeting with id {self.meeting_id} does not exist"
        super().__init__(self.message)


class AlreadyParticipantError(Exception):
    """
    Raised when trying to add user to the meeting's participants, but they are already there.
    """

    def __init__(self, meeting_id: int, user: User):
        self.meeting_id = meeting_id
        self.user = user
        self.message = f"User {self.user.email} is already a participant of meeting with id {self.meeting_id}"
