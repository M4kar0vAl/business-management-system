from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.auth.types import UserIdType
from app.teams.routers import ASSIGN_USER_ROLE_ROUTE_NAME
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestAssignUserRole(GetUrlMixin):
    url_name = ASSIGN_USER_ROLE_ROUTE_NAME
    role_to_update = Role.MANAGER
    role_json = {"role": role_to_update}  # noqa: RUF012

    def get_url(self, user_id: UserIdType):
        return super().get_url(user_id=user_id)

    async def test_assign_user_role(
        self, async_client, create_user, create_team, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.patch(
            self.get_url(user.id),
            json=self.role_json,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user = await user_db.get(user.id)
        assert updated_user is not None
        assert updated_user.role == self.role_to_update

    async def test_assign_user_role_unauthenticated(
        self, async_client, create_user, create_team
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN)
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.patch(self.get_url(user.id), json=self.role_json)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_assign_user_role_inactive(
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
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.patch(
            self.get_url(user.id),
            json=self.role_json,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_assign_user_role_not_an_admin(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.patch(
            self.get_url(user.id),
            json=self.role_json,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_assign_user_role_admin_role_is_not_assignable(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.patch(
            self.get_url(user.id),
            json={"role": Role.ADMIN},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_assign_user_role_user_not_in_team(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.patch(
            self.get_url(user.id),
            json=self.role_json,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_assign_user_role_user_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.patch(
            self.get_url(0),
            json=self.role_json,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
