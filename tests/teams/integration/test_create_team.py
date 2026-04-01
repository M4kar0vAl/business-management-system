from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.teams.routers import CREATE_TEAM_ROUTE_NAME
from app.teams.schemas import TeamCreate, TeamRead
from tests.mixins import GetUrlMixin


class TestCreateTeam(GetUrlMixin):
    url_name = CREATE_TEAM_ROUTE_NAME
    create_data = TeamCreate(name="team").model_dump()

    async def test_create_team(
        self, async_client, create_user, get_authorization_header, team_repository
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(),
            json=self.create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        created_team = await team_repository.get_by_id(data["id"])
        assert created_team is not None

        assert TeamRead.model_validate(created_team).model_dump() == data

    async def test_create_team_unauthenticated(self, async_client):
        response = await async_client.post(self.get_url(), json=self.create_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_team_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.ADMIN,
                is_active=False,
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(),
            json=self.create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_team_not_an_admin(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.post(
            self.get_url(),
            json=self.create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_team_already_exists(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        await create_team(TeamCreate(**self.create_data))

        response = await async_client.post(
            self.get_url(),
            json=self.create_data,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
