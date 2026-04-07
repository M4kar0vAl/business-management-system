from fastapi import status

from app.meetings.exceptions import (
    AlreadyParticipantError,
    MeetingDoesNotExistError,
    OverlappingMeetingError,
)

exception_status_mapping = {
    OverlappingMeetingError: status.HTTP_400_BAD_REQUEST,
    MeetingDoesNotExistError: status.HTTP_404_NOT_FOUND,
    AlreadyParticipantError: status.HTTP_400_BAD_REQUEST,
}
