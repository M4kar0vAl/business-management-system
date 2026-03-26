import pytest
from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate, UserUpdate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestUpdateCurrentUser(GetUrlMixin):
    url_name = "users:patch_current_user"

    async def test_update_current_user(
        self, async_client, create_user, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        user_update_dict = UserUpdate(email="another@example.com").model_dump(
            exclude_unset=True
        )

        response = await async_client.patch(
            self.get_url(),
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

    async def test_update_current_user_unauthorized(self, async_client, create_user):
        await create_user(UserCreate(email="user@example.com", password="Pass!234"))

        response = await async_client.patch(
            self.get_url(), json={"email": "another@example.com"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_current_user_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )

        response = await async_client.patch(
            self.get_url(),
            json={"email": "another@example.com"},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_current_user_already_exists(
        self, async_client, create_user, get_authorization_header
    ):
        another_user_email = "another@example.com"
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        await create_user(UserCreate(email=another_user_email, password="Pass!234"))

        response = await async_client.patch(
            self.get_url(),
            json={"email": another_user_email},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_current_user_invalid_password(
        self, async_client, create_user, get_authorization_header
    ):
        user_create = UserCreate(email="user@example.com", password="Pass!234")
        _, token = await create_user(user_create, authenticate=True)

        passwords_to_check = (
            "simple",  # simple password
            f"Pass!234{user_create.email}",  # email in password
        )

        for password in passwords_to_check:
            response = await async_client.patch(
                self.get_url(),
                json={"password": password},
                headers=get_authorization_header(token),
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_current_user_ignores_unsafe_fields(
        self, async_client, create_user, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        user_update_dict = UserUpdate(
            is_active=False, is_verified=True, is_superuser=True, role=Role.ADMIN
        ).model_dump(exclude_unset=True)

        response = await async_client.patch(
            self.get_url(),
            json=user_update_dict,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        user_in_db = await user_db.get(user.id)
        assert user_in_db is not None

        data = response.json()

        for field, value in user_update_dict.items():
            assert data.get(field) is not value
            assert getattr(user_in_db, field) is not value
