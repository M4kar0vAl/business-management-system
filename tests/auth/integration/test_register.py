from fastapi import status
from fastapi_users.password import PasswordHelper

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.main import app

password_helper = PasswordHelper()


class TestRegister:
    url = app.url_path_for("register:register")

    async def test_register(self, async_client, user_db):
        email = "user@example.com"
        password = "Pass!234"

        # check that user does not exist
        assert await user_db.get_by_email(email) is None

        response = await async_client.post(
            self.url, json=UserCreate(email=email, password=password).model_dump()
        )

        assert response.status_code == status.HTTP_201_CREATED

        # check that user was created
        user = await user_db.get_by_email(email)
        assert user is not None

        data = response.json()
        assert "hashed_password" not in data
        assert user.id == data["id"]

        is_password_valid, _ = password_helper.verify_and_update(
            password, user.hashed_password
        )
        assert is_password_valid

    async def test_register_already_exists(self, async_client, create_user):
        user_create = UserCreate(email="user@example.com", password="Pass!234")
        await create_user(user_create)

        response = await async_client.post(self.url, json=user_create.model_dump())

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def register_invalid_password(self, async_client):
        user_create = UserCreate(email="user@example.com", password="simple")

        response = await async_client.post(self.url, json=user_create.model_dump())

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_register_ignores_unsafe_fields(self, async_client, user_db):
        unsafe_fields = {
            "is_active": False,
            "is_verified": True,
            "is_superuser": True,
            "role": Role.ADMIN,
        }
        user_create = UserCreate(
            email="user@example.com", password="Pass!234", **unsafe_fields
        )

        response = await async_client.post(self.url, json=user_create.model_dump())

        assert response.status_code == status.HTTP_201_CREATED

        user = await user_db.get_by_email(user_create.email)
        assert user is not None

        data = response.json()
        for field, value in unsafe_fields.items():
            assert data[field] is not value
            assert getattr(user, field) is not value
