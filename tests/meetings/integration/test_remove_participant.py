from datetime import UTC, datetime, timedelta
from functools import cached_property

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.auth.types import UserIdType
from app.meetings.routers import REMOVE_MEETING_PARTICIPANT_ROUTE_NAME
from app.meetings.schemas import MeetingCreate
from tests.mixins import GetUrlMixin


class TestRemoveMeetingParticipant(GetUrlMixin):
    url_name = REMOVE_MEETING_PARTICIPANT_ROUTE_NAME

    def get_url(self, meeting_id: int, participant_id: UserIdType):
        return super().get_url(meeting_id=meeting_id, participant_id=participant_id)

    @cached_property
    def _meeting_create(self) -> MeetingCreate:
        now = datetime.now(UTC)
        return MeetingCreate(start_time=now, end_time=now + timedelta(hours=1))

    async def test_remove_meeting_participant(
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
        meeting = await create_meeting(self._meeting_create, user, participants=[user])

        response = await async_client.delete(
            self.get_url(meeting.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        meeting = await meeting_repository.get_by_id(meeting.id)
        assert meeting is not None
        assert not await meeting_repository.is_participant(meeting, user)

    async def test_remove_meeting_participant_unauthenticated(
        self, async_client, create_user, create_meeting
    ):
        user, _ = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
            ),
        )
        meeting = await create_meeting(self._meeting_create, user, participants=[user])

        response = await async_client.delete(
            self.get_url(meeting.id, user.id),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_remove_meeting_participant_inactive(
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
        meeting = await create_meeting(self._meeting_create, user, participants=[user])

        response = await async_client.delete(
            self.get_url(meeting.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_remove_meeting_participant_non_manager(
        self, async_client, create_user, create_meeting, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
            ),
            authenticate=True,
        )
        meeting = await create_meeting(self._meeting_create, user, participants=[user])

        response = await async_client.delete(
            self.get_url(meeting.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_remove_meeting_participant_meeting_does_not_exist(
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

        response = await async_client.delete(
            self.get_url(0, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_remove_meeting_participant_user_does_not_exist(
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

        response = await async_client.delete(
            self.get_url(meeting.id, 0),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_remove_meeting_participant_not_participating(
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

        response = await async_client.delete(
            self.get_url(meeting.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK
        assert not await meeting_repository.is_participant(meeting, user)
