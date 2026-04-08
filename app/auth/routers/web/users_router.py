from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi_users import exceptions

from app.auth.dependencies import get_user_manager
from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.auth.schemas import UserUpdate
from app.auth.user_manager import UserManager
from app.templates import templates

router = APIRouter(prefix="/users")

PROFILE_PAGE_ROUTE_NAME = "profile"
PROFILE_UPDATE_ROUTE_NAME = "profile:update"


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
