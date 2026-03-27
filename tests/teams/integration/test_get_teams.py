import pytest
from fastapi import status

from app.auth.schemas import UserCreate
from app.teams.routers import GET_TEAMS_ROUTE_NAME
from app.teams.schemas import TeamCreate, TeamRead
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestGetTeams(GetUrlMixin):
    url_name = GET_TEAMS_ROUTE_NAME

    async def test_get_teams(
        self, async_client, create_team, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team1 = await create_team(TeamCreate(name="team1"))
        team2 = await create_team(TeamCreate(name="team2"))

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert TeamRead.model_validate(team1).model_dump() in data
        assert TeamRead.model_validate(team2).model_dump() in data

    async def test_get_teams_unauthenticated(self, async_client):
        response = await async_client.get(self.get_url())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_teams_inactive(
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
