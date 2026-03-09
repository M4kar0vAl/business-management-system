from fastapi_users import BaseUserManager, IntegerIDMixin

from app.config import settings

from .models import User
from .types import UserIdType


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = (
        settings.ACCESS_TOKEN.RESET_PASSWORD_TOKEN_SECRET.get_secret_value()
    )
    verification_token_secret = (
        settings.ACCESS_TOKEN.VERIFICATION_TOKEN_SECRET.get_secret_value()
    )
