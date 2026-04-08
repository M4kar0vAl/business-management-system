from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.templates import templates

router = APIRouter(prefix="/users")

PROFILE_PAGE_ROUTE_NAME = "profile"


@router.get("/me", response_class=HTMLResponse, name=PROFILE_PAGE_ROUTE_NAME)
async def profile(
    user: Annotated[User, Depends(current_active_user)], request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="users/profile.html",
        context={"title": "Profile", "current_user": user},
    )
