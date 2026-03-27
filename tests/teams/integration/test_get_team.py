import pytest
from fastapi import status

from app.auth.schemas import UserCreate
from app.teams.routers import GET_TEAM_ROUTE_NAME
from app.teams.schemas import TeamCreate, TeamReadFull
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestGetTeam(GetUrlMixin):
    url_name = GET_TEAM_ROUTE_NAME

    def get_url(self, team_id: int):
        return super().get_url(team_id=team_id)

    async def test_get_team(
        self, async_client, create_team, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK
        assert TeamReadFull.model_validate(team).model_dump() == response.json()

    async def test_get_team_unauthenticated(self, async_client, create_team):
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.get(self.get_url(team.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_team_inactive(
        self, async_client, create_team, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_team_not_found(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.get(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
