from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.teams.dependencies import TeamServiceDep
from app.templates import templates

router = APIRouter(prefix="/teams")

TEAMS_LIST_PAGE_ROUTE_NAME = "teams:list_page"


@router.get("/", response_class=HTMLResponse, name=TEAMS_LIST_PAGE_ROUTE_NAME)
async def list_teams_page(
    user: Annotated[User, Depends(current_active_user)],
    teams_service: TeamServiceDep,
    request: Request,
):
    teams = await teams_service.get_all_teams()

    return templates.TemplateResponse(
        request=request,
        name="teams/list.html",
        context={"title": "Teams", "current_user": user, "teams": teams},
    )
