from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.auth.fastapi_users_instance import current_active_user_or_none
from app.auth.models import User
from app.templates import templates

router = APIRouter()


@router.get("/", name="home", response_class=HTMLResponse)
async def index(
    current_user: Annotated[User, Depends(current_active_user_or_none)],
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"current_user": current_user, "title": "Home"},
    )
