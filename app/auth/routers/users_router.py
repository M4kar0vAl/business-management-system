from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app import responses
from app.auth.dependencies import get_user_manager
from app.auth.fastapi_users_instance import fastapi_users_instance, get_current_admin
from app.auth.schemas import UserRead, UserUpdate
from app.auth.services import list_users
from app.auth.types import UserIdType
from app.auth.user_manager import UserManager
from app.dependencies import UOWDep

fastapi_users_router = fastapi_users_instance.get_users_router(UserRead, UserUpdate)

ROUTE_NAME_PREFIX = "users"
DELETE_USER_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:delete_user"
GET_USERS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:list"

# When using routes param directly, prefix and tags (and maybe smth else) are not applied.
# Exclude DELETE /users/{id} route because its permissions do not suit
fastapi_users_router_without_delete = APIRouter(
    routes=[
        route
        for route in fastapi_users_router.routes
        if route.name != DELETE_USER_ROUTE_NAME
    ]
)

router = APIRouter(
    prefix="/users", tags=["Users"], responses={**responses.UNAUTHORIZED_RESPONSE}
)
router.include_router(fastapi_users_router_without_delete)


# define user delete route with necessary permissions
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
    responses={
        **responses.FORBIDDEN_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
    },
    name=DELETE_USER_ROUTE_NAME,
)
async def delete_user(
    user_id: UserIdType,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
):
    """
    Delete a user by id.

    In order to delete a user:
    - user with id `user_id` must exist

    Active admin or superuser only
    """
    user_to_delete = await user_manager.get(user_id)

    await user_manager.delete(user_to_delete, request)


@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(get_current_admin)],
    responses={**responses.FORBIDDEN_RESPONSE},
    name=GET_USERS_ROUTE_NAME,
)
async def get_users(uow: UOWDep):
    """
    Get all users

    Active admin or superuser only.
    """
    return await list_users(uow.session)
