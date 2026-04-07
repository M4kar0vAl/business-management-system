from datetime import UTC, datetime, timedelta
from functools import cached_property

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.meetings.routers import DELETE_MEETING_ROUTE_NAME
from app.meetings.schemas import MeetingCreate
from tests.mixins import GetUrlMixin


class TestDeleteMeeting(GetUrlMixin):
    url_name = DELETE_MEETING_ROUTE_NAME

    def get_url(self, meeting_id: int):
        return super().get_url(meeting_id=meeting_id)

    @cached_property
    def _meeting_create(self) -> MeetingCreate:
        now = datetime.now(UTC)
        return MeetingCreate(start_time=now, end_time=now + timedelta(hours=1))

    async def test_delete_meeting(
        self,
        async_client,
        create_user,
        create_meeting,
        meeting_repository,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.delete(
            self.get_url(meeting.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_meeting = await meeting_repository.get_by_id(meeting.id)
        assert deleted_meeting is None

    async def test_delete_meeting_unauthenticated(
        self, async_client, create_user, create_meeting
    ):
        user, _ = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.delete(self.get_url(meeting.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_meeting_inactive(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
                is_active=False,
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.delete(
            self.get_url(meeting.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_meeting_not_an_author(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
            authenticate=True,
        )
        another_user, _ = await create_user(
            UserCreate(
                email="user1@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
        )
        meeting = await create_meeting(self._meeting_create, another_user)

        response = await async_client.delete(
            self.get_url(meeting.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_meeting_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
            authenticate=True,
        )

        response = await async_client.delete(
            self.get_url(0),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
