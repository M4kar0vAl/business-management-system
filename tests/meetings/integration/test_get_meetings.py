import json
from datetime import UTC, datetime, timedelta
from functools import cached_property

from fastapi import status

from app.auth.schemas import UserCreate
from app.meetings.routers import GET_MEETINGS_ROUTE_NAME
from app.meetings.schemas import MeetingCreate, MeetingRead
from tests.mixins import GetUrlMixin


class TestGetMeetings(GetUrlMixin):
    url_name = GET_MEETINGS_ROUTE_NAME

    @cached_property
    def _today_meeting_create(self) -> MeetingCreate:
        now = datetime.now(UTC)
        return MeetingCreate(start_time=now, end_time=now + timedelta(hours=1))

    @cached_property
    def _tomorrow_meeting_create(self) -> MeetingCreate:
        start = self._today_meeting_create.end_time + timedelta(days=1)
        return MeetingCreate(start_time=start, end_time=start + timedelta(hours=1))

    @cached_property
    def _day_after_tomorrow_meeting_create(self) -> MeetingCreate:
        start = self._tomorrow_meeting_create.end_time + timedelta(days=1)
        return MeetingCreate(start_time=start, end_time=start + timedelta(hours=1))

    async def test_get_meetings(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        another_user, _ = await create_user(
            UserCreate(email="user1@example.com", password="Pass!234")
        )
        today_meeting = await create_meeting(self._today_meeting_create, user)
        tomorrow_meeting = await create_meeting(self._tomorrow_meeting_create, user)
        day_after_tomorrow_meeting = await create_meeting(
            self._day_after_tomorrow_meeting_create, another_user
        )

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert (
            json.loads(MeetingRead.model_validate(today_meeting).model_dump_json())
            in data
        )
        assert (
            json.loads(MeetingRead.model_validate(tomorrow_meeting).model_dump_json())
            in data
        )
        assert (
            json.loads(
                MeetingRead.model_validate(day_after_tomorrow_meeting).model_dump_json()
            )
            in data
        )

    async def test_get_meetings_unauthenticated(self, async_client):
        response = await async_client.get(self.get_url())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_meetings_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_meetings_for_period(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        today_meeting = await create_meeting(self._today_meeting_create, user)
        tomorrow_meeting = await create_meeting(self._tomorrow_meeting_create, user)
        day_after_tomorrow_meeting = await create_meeting(
            self._day_after_tomorrow_meeting_create, user
        )

        # filters by start_time date inclusive
        params = {
            "start": self._today_meeting_create.start_time.date().isoformat(),
            "end": self._tomorrow_meeting_create.start_time.date().isoformat(),
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
            in data
        )
        assert (
            json.loads(
                MeetingRead.model_validate(day_after_tomorrow_meeting).model_dump_json()
            )
            not in data
        )

    async def test_get_meetings_for_period_start_in_future(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        params = {
            "start": (self._tomorrow_meeting_create.start_time.date()).isoformat(),
        }

        response = await async_client.get(
            self.get_url(), params=params, headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
