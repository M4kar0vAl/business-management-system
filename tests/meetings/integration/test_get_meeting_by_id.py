import json
from datetime import UTC, datetime, timedelta
from functools import cached_property

from fastapi import status

from app.auth.schemas import UserCreate
from app.meetings.routers import GET_MEETING_BY_ID_ROUTE_NAME
from app.meetings.schemas import MeetingCreate, MeetingReadFull
from tests.mixins import GetUrlMixin


class TestGetMeetingById(GetUrlMixin):
    url_name = GET_MEETING_BY_ID_ROUTE_NAME

    def get_url(self, meeting_id: int):
        return super().get_url(meeting_id=meeting_id)

    @cached_property
    def _meeting_create(self) -> MeetingCreate:
        now = datetime.now(UTC)
        return MeetingCreate(start_time=now, end_time=now + timedelta(hours=1))

    async def test_get_meeting_by_id(
        self,
        async_client,
        create_user,
        create_meeting,
        meeting_repository,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.get(
            self.get_url(meeting.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        meeting = await meeting_repository.get_by_id(meeting.id, full=True)
        assert meeting is not None

        data = response.json()
        assert (
            json.loads(MeetingReadFull.model_validate(meeting).model_dump_json())
            == data
        )

    async def test_get_meeting_by_id_unauthenticated(
        self, async_client, create_user, create_meeting
    ):
        user, _ = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
            ),
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.get(self.get_url(meeting.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_meeting_by_id_inactive(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                is_active=False,
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.get(
            self.get_url(meeting.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_meeting_by_id_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
            ),
            authenticate=True,
        )

        response = await async_client.get(
            self.get_url(0),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
