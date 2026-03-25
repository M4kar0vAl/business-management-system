from pydantic import BaseModel, SecretStr
from sqlalchemy import URL as SQLA_URL


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
