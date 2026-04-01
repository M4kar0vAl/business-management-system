from fastapi import status

from app.auth.schemas import UserCreate
from app.auth.types import UserIdType
from tests.mixins import GetUrlMixin


class TestGetUser(GetUrlMixin):
    url_name = "users:user"

    def get_url(self, user_id: UserIdType):
        return super().get_url(id=user_id)

    async def test_get_user(self, async_client, create_user, get_authorization_header):
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", is_superuser=True
        )
        user, token = await create_user(user_create, authenticate=True)

        # test get self
        response = await async_client.get(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        for field, value in data.items():
            assert getattr(user, field) == value

        # test get another user
        another_user, _ = await create_user(
            UserCreate(email="another@example.com", password="Pass!234")
        )
        response = await async_client.get(
            self.get_url(another_user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        for field, value in data.items():
            assert getattr(another_user, field) == value

    async def test_get_user_unauthenticated(self, async_client, create_user):
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", is_superuser=True
        )
        user, _ = await create_user(user_create)

        response = await async_client.get(self.get_url(user.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_user_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", is_active=False
        )
        user, token = await create_user(user_create, authenticate=True)

        response = await async_client.get(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_user_not_a_superuser(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(email="user@example.com", password="Pass!234")
        user, token = await create_user(user_create, authenticate=True)

        response = await async_client.get(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_user_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", is_superuser=True
        )
        _, token = await create_user(user_create, authenticate=True)

        response = await async_client.get(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
