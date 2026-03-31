import pytest
from fastapi import status

from app.auth.schemas import UserCreate, UserRead
from app.teams.routers import GET_TEAM_MEMBERS_ROUTE_NAME
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestGetTeamMembers(GetUrlMixin):
    url_name = GET_TEAM_MEMBERS_ROUTE_NAME

    def get_url(self, team_id: int):
        return super().get_url(team_id=team_id)

    async def test_get_team_members(
        self, async_client, create_team, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        user2, _ = await create_user(
            UserCreate(email="user2@example.com", password="Pass!234")
        )
        user3, _ = await create_user(
            UserCreate(email="user3@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team1"), members=[user, user2])

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert UserRead.model_validate(user).model_dump() in data
        assert UserRead.model_validate(user2).model_dump() in data
        assert UserRead.model_validate(user3).model_dump() not in data

    async def test_get_team_members_unauthenticated(self, async_client, create_team):
        team = await create_team(TeamCreate(name="team"))
        response = await async_client.get(self.get_url(team.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_team_members_inactive(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team1"))

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_team_members_team_not_found(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.get(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_team_members_user_not_a_member(
        self, async_client, create_team, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team1"))

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
