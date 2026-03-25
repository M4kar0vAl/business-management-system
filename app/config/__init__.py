from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import AppConfig
from .auth import AuthenticationConfig
from .db import DatabaseConfig
from .users import UserConfig

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_nested_delimiter="__", env_prefix="BMS__"
    )

    APP: AppConfig = AppConfig()
    DB: DatabaseConfig = DatabaseConfig()
    AUTHENTICATION: AuthenticationConfig = AuthenticationConfig()
    USER: UserConfig = UserConfig()


settings = Settings()
