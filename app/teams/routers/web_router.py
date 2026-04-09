from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth.fastapi_users_instance import current_active_user, get_current_admin
from app.auth.models import User
from app.teams.dependencies import TeamServiceDep, team_of_current_user
from app.teams.exceptions import TeamAlreadyExistsError
from app.teams.models import Team
from app.teams.schemas import TeamCreate
from app.templates import templates

router = APIRouter(prefix="/teams")

TEAMS_LIST_PAGE_ROUTE_NAME = "teams:list_page"
TEAMS_CREATE_PAGE_ROUTE_NAME = "teams:create_page"
TEAMS_CREATE_ROUTE_NAME = "create_team"
TEAMS_DETAIL_PAGE_ROUTE_NAME = "teams:detail_page"


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


@router.get("/create", response_class=HTMLResponse, name=TEAMS_CREATE_PAGE_ROUTE_NAME)
async def create_team_page(
    user: Annotated[User, Depends(get_current_admin)],
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="teams/create.html",
        context={
            "title": "Create Team",
            "current_user": user,
        },
    )


@router.post("/", response_class=HTMLResponse, name=TEAMS_CREATE_ROUTE_NAME)
async def create_team(
    team_data: Annotated[TeamCreate, Form()],
    user: Annotated[User, Depends(get_current_admin)],
    teams_service: TeamServiceDep,
    request: Request,
):
    try:
        await teams_service.create_team(team_data)
    except TeamAlreadyExistsError:
        error = "Team with this name already exists"
    else:
        return RedirectResponse(
            request.url_for(TEAMS_LIST_PAGE_ROUTE_NAME),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="teams/create.html",
        context={
            "title": "Create Team",
            "current_user": user,
            "team_data": team_data,
            "error": error,
        },
    )


@router.get(
    "/{team_id}", response_class=HTMLResponse, name=TEAMS_DETAIL_PAGE_ROUTE_NAME
)
async def team_detail_page(
    team: Annotated[Team, Depends(team_of_current_user(current_active_user))],
    user: Annotated[User, Depends(current_active_user)],
    teams_service: TeamServiceDep,
    request: Request,
):
    members = await teams_service.get_team_members(team)
    tasks = await teams_service.get_team_tasks(team)

    return templates.TemplateResponse(
        request=request,
        name="teams/detail.html",
        context={
            "title": f"Team {team.name}",
            "current_user": user,
            "team": team,
            "members": members,
            "tasks": tasks,
        },
    )
