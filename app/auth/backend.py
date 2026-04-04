from fastapi_users.authentication import AuthenticationBackend

from app.auth.dependencies import get_database_strategy
from app.auth.transports import bearer_transport, cookie_transport

auth_bearer_db_backend = AuthenticationBackend(
    name="bearer_db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
auth_cookie_db_backend = AuthenticationBackend(
    name="cookie_db",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
