from contextlib import asynccontextmanager

import pytest
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.actions import create_user as create_user_action
from app.auth.models import User
from app.auth.schemas import UserCreate

password_helper = PasswordHelper()


def async_test_session_context_factory(session: AsyncSession):
    @asynccontextmanager
    async def async_test_session_context():
        yield session

    return async_test_session_context


@pytest.fixture
async def patch_get_async_session_context(monkeypatch, session):
    monkeypatch.setattr(
        "app.auth.actions.get_async_session_context",
        async_test_session_context_factory(session),
    )


@pytest.mark.usefixtures("patch_get_async_session_context")
@pytest.mark.unit
class TestCreateUserAction:
    async def test_create_user(self):
        email = "user@example.com"
        password = "Pass!234"
        user = await create_user_action(email=email, password=password)

        assert isinstance(user, User)
        assert user.email == email
        assert user.is_active
        assert not user.is_verified
        assert not user.is_superuser

        is_password_valid, _ = password_helper.verify_and_update(
            password, user.hashed_password
        )
        assert is_password_valid

    async def test_create_superuser(self):
        email = "admin@example.com"
        password = "Pass!234"
        user = await create_user_action(
            email=email, password=password, is_superuser=True
        )

        assert isinstance(user, User)
        assert user.is_superuser

    async def test_create_user_invalid_password(self):
        email = "user@example.com"
        password = "simple"

        # password is too simple
        with pytest.raises(InvalidPasswordException):
            await create_user_action(email=email, password=password)

        valid_password = "Pass!234"

        # password contains email
        with pytest.raises(InvalidPasswordException):
            await create_user_action(email=email, password=f"{valid_password}{email}")

    async def test_create_user_already_exists(self, create_user):
        email = "user@example.com"
        password = "Pass!234"
        await create_user(UserCreate(email=email, password=password))

        with pytest.raises(UserAlreadyExists):
            await create_user_action(email, password)
