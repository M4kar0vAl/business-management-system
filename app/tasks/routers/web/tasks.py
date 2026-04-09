from datetime import UTC, datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.auth.fastapi_users_instance import get_current_manager
from app.auth.models import User
from app.tasks.dependencies import TaskServiceDep
from app.tasks.schemas import TaskCreate
from app.teams.exceptions import TeamDoesNotExistError, UserDoesNotBelongToTeamError
from app.teams.routers.web_router import TEAMS_DETAIL_PAGE_ROUTE_NAME
from app.templates import templates

router = APIRouter()

CREATE_TASK_PAGE_ROUTE_NAME = "tasks:create_page"
CREATE_TASK_ROUTE_NAME = "create_task"


@router.get("/teams/{team_id}/create_task", name=CREATE_TASK_PAGE_ROUTE_NAME)
async def create_task_page(
    team_id: int,
    user: Annotated[User, Depends(get_current_manager)],
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="tasks/create.html",
        context={
            "title": "Create Task",
            "current_user": user,
            "team_id": team_id,
        },
    )


@router.post("/", name=CREATE_TASK_ROUTE_NAME)
async def create_task(
    description: Annotated[str, Form()],
    deadline: Annotated[datetime, Form()],
    team_id: Annotated[int, Form()],
    user_timezone: Annotated[str, Form()],
    user: Annotated[User, Depends(get_current_manager)],
    task_service: TaskServiceDep,
    request: Request,
):
    user_tz = pytz.timezone(user_timezone)

    try:
        task_data = TaskCreate(
            description=description,
            deadline=user_tz.localize(deadline).astimezone(UTC),
            team_id=team_id,
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            request=request,
            name="tasks/create.html",
            context={
                "title": "Create Task",
                "current_user": user,
                "team_id": team_id,
                "error": e,
            },
        )

    try:
        await task_service.create_task(task_data, user)
    except UserDoesNotBelongToTeamError:
        error = "User does not belong to team"
    except TeamDoesNotExistError:
        error = "Team does not exist"
    else:
        return RedirectResponse(
            request.url_for(TEAMS_DETAIL_PAGE_ROUTE_NAME, team_id=task_data.team_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="tasks/create.html",
        context={
            "title": "Create Task",
            "current_user": user,
            "team_id": task_data.team_id,
            "task_data": task_data,
            "error": error,
        },
    )
