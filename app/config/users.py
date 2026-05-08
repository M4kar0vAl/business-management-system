import re
from functools import cached_property

from pydantic import BaseModel, EmailStr, SecretStr


class PasswordConfig(BaseModel):
    MIN_LENGTH: int = 8
    LOWERCASE_MIN_NUMBER: int = 1
    UPPERCASE_MIN_NUMBER: int = 1
    DIGITS_MIN_NUMBER: int = 1
    SPECIAL_CHARS_MIN_NUMBER: int = 1
    ALLOWED_SPECIAL_CHARS: str = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

    @cached_property
    def REGEXP(self) -> re.Pattern:
        return re.compile(
            rf"^"
            rf"(?=(.*[a-z]){{{self.LOWERCASE_MIN_NUMBER},}})"  # lowercase letters
            rf"(?=(.*[A-Z]){{{self.UPPERCASE_MIN_NUMBER},}})"  # uppercase letters
            rf"(?=(.*[0-9]){{{self.DIGITS_MIN_NUMBER},}})"  # digits
            rf"(?=(.*[{re.escape(self.ALLOWED_SPECIAL_CHARS)}])"  # special characters
            rf"{{{self.SPECIAL_CHARS_MIN_NUMBER},}})"  # min number of special characters
            rf".{{{self.MIN_LENGTH},}}"  # min length
            rf"$"
        )


class UserConfig(BaseModel):
    ADMIN_EMAIL: EmailStr = "admin@example.com"
    ADMIN_PASSWORD: SecretStr = SecretStr("Pass!1234")
    PASSWORD: PasswordConfig = PasswordConfig()
