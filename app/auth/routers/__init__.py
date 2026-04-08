__all__ = ["auth_router", "users_router", "web_auth_router", "web_users_router"]

from .api.auth_router import router as auth_router
from .api.users_router import router as users_router
from .web.auth_router import router as web_auth_router
from .web.users_router import router as web_users_router
