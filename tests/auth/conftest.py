import pytest
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.backend import authentication_backend
from app.auth.models import AccessToken


@pytest.fixture
async def access_token_db(session):
    return AccessToken.get_db(session)


@pytest.fixture
async def authenticate_user(access_token_db, user_manager):
    async def _authenticate_user(email, password):
        user = await user_manager.authenticate(
            OAuth2PasswordRequestForm(username=email, password=password)
        )

        assert user is not None, f"Could not authenticate user {email}"

        strategy = authentication_backend.get_strategy(access_token_db)
        token = await strategy.write_token(user)

        return user, token

    return _authenticate_user


@pytest.fixture(scope="session")
def get_authorization_header():

    def _get_authorization_header(token):
        return {
            "Authorization": f"Bearer {token}",
        }

    return _get_authorization_header
