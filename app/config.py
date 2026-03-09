from pathlib import Path

from pydantic import BaseModel, SecretStr
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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_nested_delimiter="__", env_prefix="BMS__"
    )

    APP: AppConfig = AppConfig()
    DB: DatabaseConfig = DatabaseConfig()
    AUTHENTICATION: AuthenticationConfig = AuthenticationConfig()


settings = Settings()
