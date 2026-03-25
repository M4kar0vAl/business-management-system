from pydantic import BaseModel, SecretStr


class AuthenticationConfig(BaseModel):
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 604800  # 7 days
    RESET_PASSWORD_TOKEN_SECRET: SecretStr = "secret"
    VERIFICATION_TOKEN_SECRET: SecretStr = "secret"
    ADMIN_PANEL_SECRET_KEY: SecretStr = "secret"
