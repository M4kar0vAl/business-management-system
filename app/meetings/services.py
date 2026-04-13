from pydantic import EmailStr

from app.auth.models import User
from app.auth.types import UserIdType
from app.auth.user_manager import UserManager
from app.meetings.exceptions import (
    AlreadyParticipantError,
    MeetingDoesNotExistError,
    OverlappingMeetingError,
)
from app.meetings.models import Meeting
from app.meetings.repositories import MeetingRepository
from app.meetings.schemas import MeetingCreate, MeetingFilters, MeetingsCalendarFilters
from app.uow import UnitOfWork


class MeetingService:
    def __init__(self, uow: UnitOfWork, user_manager: UserManager):
        self.uow = uow
        self.meetings_repo = MeetingRepository(self.uow.session)
        self.user_manager = user_manager

    async def create_meeting(self, meeting: MeetingCreate, user: User) -> Meeting:
        """
        Create a new meeting.

        :param meeting: data to create meeting with
        :param user: user who is creating the meeting
        :return: created Meeting instance
        :raises OverlappingMeetingError: if the meeting time overlaps with another meeting
        """
        if await self.meetings_repo.is_overlapping(
            meeting.start_time, meeting.end_time
        ):
            raise OverlappingMeetingError(meeting.start_time, meeting.end_time)

        return await self.meetings_repo.create(meeting, user)

    async def get_meeting_by_id(self, meeting_id: int, full: bool = False) -> Meeting:
        """
        Get meeting by id.

        :param meeting_id: id of a meeting to get
        :param full: boolean indicating whether to return meeting with all relations
        :return: meeting instance or None if it was not found
        :raises MeetingDoesNotExistError: if the meeting with the given id does not exist
        """
        meeting = await self.meetings_repo.get_by_id(meeting_id, full=full)

        if not meeting:
            raise MeetingDoesNotExistError(meeting_id)

        return meeting

    async def get_meetings_list(self, filters: MeetingFilters) -> list[Meeting]:
        """
        Get list of meetings.

        :param filters: filters to apply
        :return: list of meetings
        """
        return await self.meetings_repo.get_list(filters)

    async def get_user_meetings(
        self, user: User, filters: MeetingFilters
    ) -> list[Meeting]:
        """
        Get list of meetings where a user is participant.

        :param user: user to get meetings of
        :param filters: filters to apply
        :return: list of user meetings
        """
        return await self.meetings_repo.get_user_meetings(user, filters)

    async def get_meetings_calendar(
        self, filters: MeetingsCalendarFilters
    ) -> list[Meeting]:
        """
        Get meetings to display in calendar.

        :param filters: filters to apply, including calendar period.
        :return: list of meetings
        """
        return await self.meetings_repo.get_meetings_calendar(filters)

    async def delete_meeting(self, meeting: Meeting) -> None:
        """
        Delete a meeting.

        :param meeting: meeting to delete
        :return: None
        """
        await self.meetings_repo.delete(meeting)

    async def add_participant(self, meeting: Meeting, user_email: EmailStr) -> None:
        """
        Add a participant to a meeting.

        :param meeting: meeting to add the participant to
        :param user_email: email of a user to add to the meeting
        :return: None
        :raises UserNotExists: if the user with the given email does not exist
        :raises AlreadyParticipantError: if the user is already a participant of the meeting
        """
        user = await self.user_manager.get_by_email(user_email)

        if await self.meetings_repo.is_participant(meeting, user):
            raise AlreadyParticipantError(meeting.id, user)

        await self.meetings_repo.add_participant(meeting, user)

    async def remove_participant(self, meeting: Meeting, user_id: UserIdType) -> None:
        """
        Remove a participant from a meeting.

        :param meeting: meeting to remove the participant from
        :param user_id: id of a user to remove from the meeting
        :return: None
        :raises UserNotExists: if the user with the given email does not exist
        """
        user = await self.user_manager.get(user_id)

        await self.meetings_repo.remove_participant(meeting, user)
