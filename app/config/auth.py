from typing import Literal

from pydantic import BaseModel, SecretStr


class CookieAuthConfig(BaseModel):
    NAME: str = "fastapiusersauth"
    MAX_AGE: int | None = 604800  # 7 days
    PATH: str = "/"
    DOMAIN: str | None = None
    SECURE: bool = False
    HTTPONLY: bool = True
    SAMESITE: Literal["lax", "strict", "none"] = "lax"


class AuthenticationConfig(BaseModel):
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 604800  # 7 days
    RESET_PASSWORD_TOKEN_SECRET: SecretStr = "secret"
    VERIFICATION_TOKEN_SECRET: SecretStr = "secret"
    ADMIN_PANEL_SECRET_KEY: SecretStr = "secret"
    COOKIE: CookieAuthConfig = CookieAuthConfig()
