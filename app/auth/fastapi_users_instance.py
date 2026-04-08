from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import FastAPIUsers

from ..http_exceptions import ForbiddenError, RedirectException
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


async def unauthenticated_user_or_redirect_home(
    user: Annotated[User | None, Depends(current_active_user_or_none)], request: Request
):
    """
    Dependency to ensure that current user is unauthenticated. Otherwise, redirects to home page.

    :param user: user performing the action or None if there is no authenticated user
    :param request: fastapi request object
    :return: None
    :raises RedirectException: if the user is authenticated. Redirects to home page
    """
    if user is None:
        return

    raise RedirectException(request.url_for("home"))


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
