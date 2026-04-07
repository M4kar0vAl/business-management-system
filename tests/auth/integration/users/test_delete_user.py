from fastapi import status

from app.auth.models import Role
from app.auth.routers.users_router import DELETE_USER_ROUTE_NAME
from app.auth.schemas import UserCreate
from app.auth.types import UserIdType
from tests.mixins import GetUrlMixin


class TestDeleteUser(GetUrlMixin):
    url_name = DELETE_USER_ROUTE_NAME

    def get_url(self, user_id: UserIdType):
        return super().get_url(user_id=user_id)

    async def test_delete_user(
        self, async_client, create_user, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        another_user, _ = await create_user(
            UserCreate(email="another@example.com", password="Pass!234")
        )
        authorization_header = get_authorization_header(token)

        # delete another user
        response = await async_client.delete(
            self.get_url(another_user.id), headers=authorization_header
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        user_in_db = await user_db.get(another_user.id)
        assert user_in_db is None

        # delete self
        response = await async_client.delete(
            self.get_url(user.id), headers=authorization_header
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        user_in_db = await user_db.get(user.id)
        assert user_in_db is None

    async def test_delete_user_unauthenticated(self, async_client, create_user):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN)
        )

        response = await async_client.delete(self.get_url(user.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_user_inactive(
        self, async_client, create_user, get_authorization_header
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

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_user_not_an_admin(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_user_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.delete(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
