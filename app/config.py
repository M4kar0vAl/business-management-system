import re
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL as SQLA_URL

BASE_DIR = Path(__file__).parent.parent


class AppConfig(BaseModel):
    PORT: int = 80


class DatabaseConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "user"
    PASS: SecretStr = SecretStr("password")
    NAME: str = "my_db"
    NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def URL(self) -> SQLA_URL:
        return SQLA_URL.create(
            drivername="postgresql+asyncpg",
            database=self.NAME,
            host=self.HOST,
            port=self.PORT,
            username=self.USER,
            password=self.PASS.get_secret_value(),
        )


class AuthenticationConfig(BaseModel):
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 604800  # 7 days
    RESET_PASSWORD_TOKEN_SECRET: SecretStr = "secret"
    VERIFICATION_TOKEN_SECRET: SecretStr = "secret"
    ADMIN_PANEL_SECRET_KEY: SecretStr = "secret"


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
    ADMIN_PASSWORD: SecretStr = "Pass!1234"
    PASSWORD: PasswordConfig = PasswordConfig()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_nested_delimiter="__", env_prefix="BMS__"
    )

    APP: AppConfig = AppConfig()
    DB: DatabaseConfig = DatabaseConfig()
    AUTHENTICATION: AuthenticationConfig = AuthenticationConfig()
    USER: UserConfig = UserConfig()


settings = Settings()
