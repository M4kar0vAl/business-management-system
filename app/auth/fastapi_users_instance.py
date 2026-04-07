from typing import Annotated

from fastapi import Depends
from fastapi_users import FastAPIUsers

from ..http_exceptions import ForbiddenError
from .backend import auth_bearer_db_backend, auth_cookie_db_backend
from .dependencies import get_user_manager
from .models import Role, User
from .types import UserIdType

fastapi_users_instance = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [auth_bearer_db_backend, auth_cookie_db_backend],
)


# placed these dependencies here,
# because moving them into dependencies package will cause circular import
current_active_user = fastapi_users_instance.current_user(active=True)
current_active_user_or_none = fastapi_users_instance.current_user(
    optional=True, active=True
)
current_active_superuser = fastapi_users_instance.current_user(
    active=True, superuser=True
)


async def get_current_admin(
    current_user: Annotated[User, Depends(current_active_user)],
):
    if current_user.role == Role.ADMIN or current_user.is_superuser:
        return current_user

    raise ForbiddenError()


async def get_current_manager(
    current_user: Annotated[User, Depends(current_active_user)],
):
    if (
        current_user.role == Role.MANAGER
        or current_user.role == Role.ADMIN
        or current_user.is_superuser
    ):
        return current_user

    raise ForbiddenError()
