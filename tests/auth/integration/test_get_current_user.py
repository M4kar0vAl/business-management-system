from fastapi import status

from app.auth.schemas import UserCreate
from tests.mixins import GetUrlMixin


class TestGetCurrentUser(GetUrlMixin):
    url_name = "users:current_user"

    async def test_get_current_user(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(email="user@example.com", password="Pass!234")
        user, token = await create_user(user_create, authenticate=True)

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        for field, value in data.items():
            assert getattr(user, field) == value

    async def test_get_current_user_unauthenticated(self, async_client):
        response = await async_client.get(self.get_url())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", is_active=False
        )
        _, token = await create_user(user_create, authenticate=True)

        response = await async_client.get(
            self.get_url(), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
