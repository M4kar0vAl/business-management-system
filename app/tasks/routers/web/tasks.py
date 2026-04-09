from contextlib import suppress
from datetime import UTC, datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.auth.fastapi_users_instance import current_active_user, get_current_manager
from app.auth.models import User
from app.tasks.dependencies import TaskServiceDep, current_task
from app.tasks.exceptions import UserIsNotTaskAssigneeError
from app.tasks.models import Task, TaskStatus
from app.tasks.schemas import TaskCreate
from app.teams.exceptions import TeamDoesNotExistError, UserDoesNotBelongToTeamError
from app.teams.routers.web_router import TEAMS_DETAIL_PAGE_ROUTE_NAME
from app.templates import templates

router = APIRouter()

CREATE_TASK_PAGE_ROUTE_NAME = "tasks:create_page"
CREATE_TASK_ROUTE_NAME = "create_task"
DELETE_TASK_ROUTE_NAME = "delete_task"
ASSIGN_USER_TO_TASK_ROUTE_NAME = "assign_user_to_task"
UPDATE_TASK_STATUS_ROUTE_NAME = "update_task_status"


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


@router.post(
    "/teams/{team_id}/delete_task/{task_id}",
    dependencies=[Depends(get_current_manager)],
    name=DELETE_TASK_ROUTE_NAME,
)
async def delete_task(
    task: Annotated[
        Task,
        Depends(current_task(get_current_manager, task_team_member=True, author=True)),
    ],
    task_service: TaskServiceDep,
    request: Request,
):
    await task_service.delete_task(task)

    return RedirectResponse(
        request.url_for(TEAMS_DETAIL_PAGE_ROUTE_NAME, team_id=task.team_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/{task_id}/assign_user/",
    dependencies=[Depends(get_current_manager)],
    name=ASSIGN_USER_TO_TASK_ROUTE_NAME,
)
async def assign_user_to_task(
    task: Annotated[
        Task,
        Depends(current_task(get_current_manager, task_team_member=True)),
    ],
    task_service: TaskServiceDep,
    request: Request,
    assignee_id: Annotated[int | None, Form()] = None,
):
    if assignee_id is not None:
        await task_service.assign_user_to_task(task, assignee_id)
    else:
        task.assignee = None

    return RedirectResponse(
        request.url_for(TEAMS_DETAIL_PAGE_ROUTE_NAME, team_id=task.team_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/{task_id}/update_status/",
    name=UPDATE_TASK_STATUS_ROUTE_NAME,
)
async def update_task_status(
    task: Annotated[
        Task,
        Depends(current_task(current_active_user, task_team_member=True)),
    ],
    task_status: Annotated[TaskStatus, Form()],
    user: Annotated[User, Depends(current_active_user)],
    task_service: TaskServiceDep,
    request: Request,
):
    with suppress(UserIsNotTaskAssigneeError):
        await task_service.update_task_status(task, task_status, user)

    return RedirectResponse(
        request.url_for(TEAMS_DETAIL_PAGE_ROUTE_NAME, team_id=task.team_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
