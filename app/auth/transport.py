from fastapi_users.authentication import BearerTransport

# TODO: update url
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
