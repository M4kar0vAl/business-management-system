import pytest
from fastapi import status

from app.auth.backend import authentication_backend
from app.auth.schemas import UserCreate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestLogin(GetUrlMixin):
    url_name = f"auth:{authentication_backend.name}.login"

    async def test_login(self, async_client, create_user, access_token_db):
        password = "Pass!234"
        user, _ = await create_user(
            UserCreate(email="user@example.com", password=password)
        )

        response = await async_client.post(
            self.get_url(), data={"username": user.email, "password": password}
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data

        token = await access_token_db.get_by_token(data["access_token"])

        assert token is not None
        assert token.user_id == user.id

    async def test_login_user_not_active(self, async_client, create_user):
        password = "Pass!234"
        user, _ = await create_user(
            UserCreate(email="user@example.com", password=password, is_active=False)
        )

        response = await async_client.post(
            self.get_url(), data={"username": user.email, "password": password}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_login_bad_credentials(self, async_client, create_user):
        password = "Pass!234"
        user, _ = await create_user(
            UserCreate(email="user@example.com", password=password)
        )

        response = await async_client.post(
            self.get_url(), data={"username": user.email, "password": "Wr0ngP@ss"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = await async_client.post(
            self.get_url(),
            data={"username": "nonexistent@example.com", "password": password},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
