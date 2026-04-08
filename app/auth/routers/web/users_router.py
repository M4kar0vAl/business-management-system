from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi_users import exceptions

from app.auth.dependencies import get_user_manager
from app.auth.fastapi_users_instance import current_active_user, get_current_admin
from app.auth.models import User
from app.auth.schemas import UserUpdate
from app.auth.services import list_users
from app.auth.user_manager import UserManager
from app.dependencies import SessionDep
from app.http_exceptions import RedirectException
from app.templates import templates

router = APIRouter(prefix="/users")

PROFILE_PAGE_ROUTE_NAME = "profile"
PROFILE_UPDATE_ROUTE_NAME = "profile:update"
USER_LIST_PAGE_ROUTE_NAME = "users:list_page"
USER_DELETE_ROUTE_NAME = "delete_user"


@router.get("/me", response_class=HTMLResponse, name=PROFILE_PAGE_ROUTE_NAME)
async def profile(
    user: Annotated[User, Depends(current_active_user)], request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="users/profile.html",
        context={"title": "Profile", "current_user": user},
    )


@router.post("/me", response_class=HTMLResponse, name=PROFILE_UPDATE_ROUTE_NAME)
async def update_profile(
    user: Annotated[User, Depends(current_active_user)],
    update_data: Annotated[UserUpdate, Form()],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
):
    updated_user = user
    error = None
    try:
        updated_user = await user_manager.update(
            update_data, user, safe=True, request=request
        )
    except exceptions.InvalidPasswordException as e:
        error = e.reason
    except exceptions.UserAlreadyExists:
        error = "User with this email already exists"

    return templates.TemplateResponse(
        request=request,
        name="users/profile.html",
        context={"title": "Profile", "current_user": updated_user, "error": error},
    )


@router.get("/", response_class=HTMLResponse, name=USER_LIST_PAGE_ROUTE_NAME)
async def users_list_page(
    session: SessionDep,
    user: Annotated[User, Depends(get_current_admin)],
    request: Request,
):
    users = await list_users(session)

    return templates.TemplateResponse(
        request=request,
        name="users/list.html",
        context={"title": "Users", "current_user": user, "users": users},
    )


@router.post("/{user_id}", name=USER_DELETE_ROUTE_NAME)
async def delete_user(
    user_id: int,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    request: Request,
):
    try:
        user_to_delete = await user_manager.get(user_id)
        await user_manager.delete(user_to_delete, request)
    except exceptions.UserNotExists:
        pass

    raise RedirectException(request.url_for(USER_LIST_PAGE_ROUTE_NAME))
