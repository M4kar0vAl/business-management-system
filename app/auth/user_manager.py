from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
    InvalidPasswordException,
    models,
    schemas,
)

from app.config import settings

from .models import User
from .types import UserIdType


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = (
        settings.AUTHENTICATION.RESET_PASSWORD_TOKEN_SECRET.get_secret_value()
    )
    verification_token_secret = (
        settings.AUTHENTICATION.VERIFICATION_TOKEN_SECRET.get_secret_value()
    )

    async def validate_password(
        self, password: str, user: schemas.UC | models.UP
    ) -> None:
        if not settings.PASSWORD.REGEXP.match(password):
            raise InvalidPasswordException(
                reason=(
                    f"Password should be at least {settings.PASSWORD.MIN_LENGTH} characters and "
                    f"have at least {settings.PASSWORD.LOWERCASE_MIN_NUMBER} lowercase letters, "
                    f"{settings.PASSWORD.UPPERCASE_MIN_NUMBER} uppercase letters, "
                    f"{settings.PASSWORD.DIGITS_MIN_NUMBER} digits, "
                    f"{settings.PASSWORD.SPECIAL_CHARS_MIN_NUMBER} special chars. "
                    f"Special chars allowed: {settings.PASSWORD.ALLOWED_SPECIAL_CHARS}"
                )
            )

        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")
