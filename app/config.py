from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    PORT: int = 80


class DatabaseConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = "5432"
    USER: str = "user"
    PASS: SecretStr = SecretStr("password")
    NAME: str = "my_db"

    @property
    def URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASS.get_secret_value()}"
            f"@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    APP: AppConfig = AppConfig()
    DB: DatabaseConfig = DatabaseConfig()


settings = Settings()
