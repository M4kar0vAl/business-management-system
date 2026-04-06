from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.meetings.models import Meeting
from app.meetings.schemas import MeetingCreate, MeetingFilters

if TYPE_CHECKING:
    from app.auth.models import User


class MeetingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, meeting: MeetingCreate) -> Meeting:
        """
        Create a new meeting.

        :param meeting: data to create meeting with
        :return: created Meeting instance
        """
        db_meeting = Meeting(**meeting.model_dump())
        self.session.add(db_meeting)
        return db_meeting

    async def get_by_id(self, meeting_id: int, full: bool = False) -> Meeting | None:
        """
        Get meeting by id.

        :param meeting_id: id of a meeting to get
        :param full: boolean indicating whether to return meeting with all relations
        :return: meeting instance or None if it was not found
        """
        options = [joinedload(Meeting.created_by)]

        if full:
            options.append(selectinload(Meeting.participants))

        stmt = select(Meeting).where(Meeting.id == meeting_id).options(*options)
        return (await self.session.scalars(stmt)).one_or_none()

    async def get_list(self, filters: MeetingFilters) -> list[Meeting]:
        """
        Get list of meetings.

        :param filters: filters to apply
        :return: list of meetings
        """
        filters_list = self._get_filters(filters)
        stmt = (
            select(Meeting).where(*filters_list).options(joinedload(Meeting.created_by))
        )

        return list(await self.session.scalars(stmt))

    async def get_user_meetings(
        self, user: User, filters: MeetingFilters
    ) -> list[Meeting]:
        """
        Get list of meetings where a user is participant.

        :param user: user to get meetings of
        :param filters: filters to apply
        :return: list of user meetings
        """
        filters_list = self._get_filters(filters)
        stmt = (
            select(Meeting)
            .where(Meeting.participants.any(User.id == user.id), *filters_list)
            .options(joinedload(Meeting.created_by))
        )
        return list(await self.session.scalars(stmt))

    async def delete(self, meeting: Meeting) -> None:
        """
        Delete a meeting.

        :param meeting: meeting to delete
        :return: None
        """
        await self.session.delete(meeting)

    @classmethod
    async def add_participant(cls, meeting: Meeting, user: User) -> None:
        """
        Add a participant to a meeting.

        :param meeting: meeting to add the participant to
        :param user: user to add to the meeting
        :return: None
        """
        meeting.participants.append(user)

    @classmethod
    async def remove_participant(cls, meeting: Meeting, user: User) -> None:
        """
        Remove a participant from a meeting.

        :param meeting: meeting to remove the participant from
        :param user: user to remove from the meeting
        :return: None
        """
        with suppress(ValueError):
            meeting.participants.remove(user)

    @classmethod
    def _get_filters(cls, filters: MeetingFilters) -> list:
        filters_list = []

        period_start = filters.start
        if period_start is not None:
            start_datetime = datetime(
                period_start.year, period_start.month, period_start.day, tzinfo=UTC
            )
            filters_list.append(Meeting.start_time >= start_datetime)

        period_end = filters.end
        if period_end is not None:
            end_datetime_exclusive = datetime(
                period_end.year, period_end.month, period_end.day, tzinfo=UTC
            ) + timedelta(days=1)
            filters_list.append(Meeting.start_time < end_datetime_exclusive)

        return filters_list
