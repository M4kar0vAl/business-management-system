from datetime import UTC, datetime, timedelta
from functools import cached_property

from fastapi import status
from pydantic import EmailStr

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.meetings.routers import ADD_MEETING_PARTICIPANT_ROUTE_NAME
from app.meetings.schemas import MeetingCreate
from tests.mixins import GetUrlMixin


class TestAddMeetingParticipant(GetUrlMixin):
    url_name = ADD_MEETING_PARTICIPANT_ROUTE_NAME

    def get_url(self, meeting_id: int):
        return super().get_url(meeting_id=meeting_id)

    @cached_property
    def _meeting_create(self) -> MeetingCreate:
        now = datetime.now(UTC)
        return MeetingCreate(start_time=now, end_time=now + timedelta(hours=1))

    @classmethod
    def _get_request_body(cls, email: str | EmailStr):
        return {"user_email": email}

    async def test_add_meeting_participant(
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
                role=Role.MANAGER,
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.post(
            self.get_url(meeting.id),
            json=self._get_request_body(user.email),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        meeting = await meeting_repository.get_by_id(meeting.id, full=True)
        assert meeting is not None
        assert await meeting_repository.is_participant(meeting, user)

    async def test_add_meeting_participant_unauthenticated(
        self, async_client, create_user, create_meeting
    ):
        user, _ = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.post(
            self.get_url(meeting.id), json=self._get_request_body(user.email)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_add_meeting_participant_inactive(
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

        response = await async_client.post(
            self.get_url(meeting.id),
            json=self._get_request_body(user.email),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_add_meeting_participant_non_manager(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.post(
            self.get_url(meeting.id),
            json=self._get_request_body(user.email),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_add_meeting_participant_meeting_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(0),
            json=self._get_request_body(user.email),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_meeting_participant_user_does_not_exist(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user)

        response = await async_client.post(
            self.get_url(meeting.id),
            json=self._get_request_body("nonexistent@example.com"),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_meeting_participant_already_participating(
        self,
        async_client,
        create_user,
        create_meeting,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user, participants=[user])

        response = await async_client.post(
            self.get_url(meeting.id),
            json=self._get_request_body(user.email),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
