import json
from datetime import UTC, datetime, timedelta
from functools import cached_property

from fastapi import status

from app.auth.schemas import UserCreate
from app.meetings.routers import GET_MEETINGS_CALENDAR_ROUTE_NAME
from app.meetings.schemas import MeetingCreate, MeetingRead
from tests.mixins import GetUrlMixin


class TestGetMeetingsCalendar(GetUrlMixin):
    url_name = GET_MEETINGS_CALENDAR_ROUTE_NAME

    @cached_property
    def _today_meeting_create(self) -> MeetingCreate:
        now = datetime.now(UTC)
        return MeetingCreate(start_time=now, end_time=now + timedelta(hours=1))

    @cached_property
    def _tomorrow_meeting_create(self) -> MeetingCreate:
        start = self._today_meeting_create.end_time + timedelta(days=1)
        return MeetingCreate(start_time=start, end_time=start + timedelta(hours=1))

    async def test_get_meetings_calendar(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        today_meeting = await create_meeting(self._today_meeting_create, user)
        tomorrow_meeting = await create_meeting(self._tomorrow_meeting_create, user)
        params = {
            "start": self._today_meeting_create.start_time - timedelta(hours=12),
            "end": self._today_meeting_create.end_time + timedelta(hours=12),
        }

        response = await async_client.get(
            self.get_url(), params=params, headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert (
            json.loads(MeetingRead.model_validate(today_meeting).model_dump_json())
            in data
        )
        assert (
            json.loads(MeetingRead.model_validate(tomorrow_meeting).model_dump_json())
            not in data
        )

    async def test_get_meetings_calendar_unauthenticated(self, async_client):
        params = {
            "start": self._today_meeting_create.start_time - timedelta(hours=12),
            "end": self._today_meeting_create.end_time + timedelta(hours=12),
        }

        response = await async_client.get(self.get_url(), params=params)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_meetings_calendar_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        params = {
            "start": self._today_meeting_create.start_time - timedelta(hours=12),
            "end": self._today_meeting_create.end_time + timedelta(hours=12),
        }

        response = await async_client.get(
            self.get_url(), params=params, headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
