from pydantic import BaseModel


class AppConfig(BaseModel):
    PORT: int = 80
