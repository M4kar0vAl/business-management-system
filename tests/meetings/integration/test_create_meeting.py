import json
from datetime import UTC, datetime, timedelta
from functools import cached_property
from typing import Any

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.meetings.routers import CREATE_MEETING_ROUTE_NAME
from app.meetings.schemas import MeetingCreate, MeetingRead
from tests.mixins import GetUrlMixin


class TestCreateMeeting(GetUrlMixin):
    url_name = CREATE_MEETING_ROUTE_NAME

    @cached_property
    def _create_data(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        return json.loads(
            MeetingCreate(
                start_time=now, end_time=now + timedelta(hours=1)
            ).model_dump_json()
        )

    async def test_create_meeting(
        self, async_client, create_user, meeting_repository, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(),
            json=self._create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        created_meeting = await meeting_repository.get_by_id(data["id"])
        assert created_meeting is not None
        assert created_meeting.start_time == datetime.fromisoformat(
            self._create_data["start_time"]
        )
        assert created_meeting.end_time == datetime.fromisoformat(
            self._create_data["end_time"]
        )
        assert (
            json.loads(MeetingRead.model_validate(created_meeting).model_dump_json())
            == data
        )

    async def test_create_meeting_unauthenticated(self, async_client):
        response = await async_client.post(self.get_url(), json=self._create_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_meeting_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
                is_active=False,
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(),
            json=self._create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_meeting_non_manager(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.post(
            self.get_url(),
            json=self._create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_meeting_overlaps(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        await create_meeting(
            MeetingCreate(
                start_time=datetime.fromisoformat(self._create_data["start_time"])
                + timedelta(minutes=10),
                end_time=datetime.fromisoformat(self._create_data["end_time"])
                + timedelta(minutes=10),
            ),
            user,
        )

        response = await async_client.post(
            self.get_url(),
            json=self._create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
