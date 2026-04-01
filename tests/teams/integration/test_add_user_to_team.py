from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.teams.routers import ADD_USER_TO_TEAM_ROUTE_NAME
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestAddUserToTeam(GetUrlMixin):
    url_name = ADD_USER_TO_TEAM_ROUTE_NAME

    def get_url(self, team_id: int):
        return super().get_url(team_id=team_id)

    async def test_add_user_to_team(
        self, async_client, create_user, create_team, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.post(
            self.get_url(team.id),
            json={"user_email": user.email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user = await user_db.get(user.id)
        assert updated_user is not None
        assert updated_user.team_id == team.id

    async def test_add_user_to_team_unauthenticated(
        self, async_client, create_user, create_team
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN)
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.post(
            self.get_url(team.id), json={"user_email": user.email}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_add_user_to_team_inactive(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.ADMIN,
                is_active=False,
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.post(
            self.get_url(team.id),
            json={"user_email": user.email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_add_user_to_team_not_an_admin(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.post(
            self.get_url(team.id),
            json={"user_email": user.email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_add_user_to_team_team_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(0),
            json={"user_email": user.email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_user_to_team_user_does_not_exist(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.post(
            self.get_url(team.id),
            json={"user_email": "nonexistent@example.com"},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_add_user_to_team_user_already_in_team(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.post(
            self.get_url(team.id),
            json={"user_email": user.email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
