import pytest
from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate, UserUpdate
from app.auth.types import UserIdType
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestUpdateUser(GetUrlMixin):
    url_name = "users:patch_user"

    def get_url(self, user_id: UserIdType):
        return super().get_url(id=user_id)

    async def test_update_user(
        self, async_client, create_user, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", is_superuser=True
            ),
            authenticate=True,
        )
        user_update_dict = UserUpdate(email="someone@example.com").model_dump(
            exclude_unset=True
        )

        # update self
        response = await async_client.patch(
            self.get_url(user.id),
            json=user_update_dict,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        user_in_db = await user_db.get(user.id)
        assert user_in_db is not None

        data = response.json()

        for field, value in user_update_dict.items():
            assert data.get(field) == value
            assert getattr(user_in_db, field) == value

        # update someone else
        another_user, _ = await create_user(
            UserCreate(email="another@example.com", password="Pass!234")
        )
        another_user_update_dict = UserUpdate(email="test@example.com").model_dump(
            exclude_unset=True
        )

        response = await async_client.patch(
            self.get_url(another_user.id),
            json=another_user_update_dict,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        user_in_db = await user_db.get(another_user.id)
        assert user_in_db is not None

        data = response.json()

        for field, value in another_user_update_dict.items():
            assert data.get(field) == value
            assert getattr(user_in_db, field) == value

    async def test_update_user_unauthenticated(self, async_client, create_user):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_superuser=True)
        )

        response = await async_client.patch(
            self.get_url(user.id), json={"email": "another@example.com"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_user_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                is_active=False,
                is_superuser=True,
            ),
            authenticate=True,
        )

        response = await async_client.patch(
            self.get_url(user.id),
            json={"email": "another@example.com"},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_user_not_a_superuser(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"),
            authenticate=True,
        )

        response = await async_client.patch(
            self.get_url(user.id),
            json={"email": "another@example.com"},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_user_already_exists(
        self, async_client, create_user, get_authorization_header
    ):
        another_user_email = "another@example.com"
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", is_superuser=True
            ),
            authenticate=True,
        )
        await create_user(UserCreate(email=another_user_email, password="Pass!234"))

        response = await async_client.patch(
            self.get_url(user.id),
            json={"email": another_user_email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_user_invalid_password(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", is_superuser=True
        )
        user, token = await create_user(user_create, authenticate=True)

        passwords_to_check = (
            "simple",  # simple password
            f"Pass!234{user_create.email}",  # email in password
        )

        for password in passwords_to_check:
            response = await async_client.patch(
                self.get_url(user.id),
                json={"password": password},
                headers=get_authorization_header(token),
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_user_updates_unsafe_fields(
        self, async_client, create_user, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", is_superuser=True
            ),
            authenticate=True,
        )
        user_update_dict = UserUpdate(
            is_active=False, is_verified=True, is_superuser=True, role=Role.ADMIN
        ).model_dump(exclude_unset=True)

        response = await async_client.patch(
            self.get_url(user.id),
            json=user_update_dict,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        user_in_db = await user_db.get(user.id)
        assert user_in_db is not None

        data = response.json()

        for field, value in user_update_dict.items():
            assert data.get(field) == value
            assert getattr(user_in_db, field) == value
