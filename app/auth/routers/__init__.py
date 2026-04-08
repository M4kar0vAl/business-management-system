__all__ = ["auth_router", "users_router"]

from .auth_router import router as auth_router
from .users_router import router as users_router
from .api.auth_router import router as auth_router
from .api.users_router import router as users_router
