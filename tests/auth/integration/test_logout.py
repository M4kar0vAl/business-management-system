from fastapi import status

from app.auth.backend import authentication_backend
from app.auth.schemas import UserCreate
from app.main import app


class TestLogout:
    url = app.url_path_for(f"auth:{authentication_backend.name}.logout")

    async def test_logout(
        self, async_client, create_user, access_token_db, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.post(
            self.url, headers=get_authorization_header(token)
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        token = await access_token_db.get_by_token(token)
        assert token is None

    async def test_logout_unauthenticated(self, async_client):
        response = await async_client.post(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_logout_inactive_user(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )

        response = await async_client.post(
            self.url, headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
