from fastapi import status

from app.auth.models import Role
from app.auth.routers.api.users_router import GET_USERS_ROUTE_NAME
from app.auth.schemas import UserCreate, UserRead
from tests.mixins import GetUrlMixin


class TestGetUsers(GetUrlMixin):
    url_name = GET_USERS_ROUTE_NAME

    async def test_get_users(self, async_client, create_user, get_authorization_header):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        another_user, _ = await create_user(
            UserCreate(email="user1@example.com", password="Pass!234")
        )
        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert UserRead.model_validate(user).model_dump() in data
        assert UserRead.model_validate(another_user).model_dump() in data

    async def test_get_users_unauthenticated(self, async_client):
        response = await async_client.get(self.get_url())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_users_inactive(
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

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_users_not_an_admin(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
