from contextlib import suppress
from datetime import UTC, datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.auth.fastapi_users_instance import current_active_user, get_current_manager
from app.auth.models import Role, User
from app.tasks.dependencies import (
    CommentServiceDep,
    EvaluationServiceDep,
    TaskServiceDep,
    current_task,
)
from app.tasks.exceptions import UserIsNotTaskAssigneeError
from app.tasks.models import Task, TaskStatus
from app.tasks.schemas import EvaluationsFilters, TaskCreate, TaskUpdate
from app.teams.dependencies import TeamServiceDep
from app.teams.exceptions import TeamDoesNotExistError, UserDoesNotBelongToTeamError
from app.teams.routers.web_router import (
    TEAMS_DETAIL_PAGE_ROUTE_NAME,
    TEAMS_LIST_PAGE_ROUTE_NAME,
)
from app.templates import templates

router = APIRouter()

CREATE_TASK_PAGE_ROUTE_NAME = "tasks:create_page"
CREATE_TASK_ROUTE_NAME = "create_task"
DELETE_TASK_ROUTE_NAME = "delete_task"
ASSIGN_USER_TO_TASK_ROUTE_NAME = "assign_user_to_task"
UPDATE_TASK_STATUS_ROUTE_NAME = "update_task_status"
DETAIL_TASK_PAGE_ROUTE_NAME = "tasks:detail_page"
EDIT_TASK_PAGE_ROUTE_NAME = "tasks:edit_page"
UPDATE_TASK_ROUTE_NAME = "update_task"


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


@router.get("/{task_id}", name=DETAIL_TASK_PAGE_ROUTE_NAME)
async def task_detail_page(
    task: Annotated[
        Task,
        Depends(current_task(current_active_user, task_team_member=True, full=True)),
    ],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
    team_service: TeamServiceDep,
    comment_service: CommentServiceDep,
    evaluation_service: EvaluationServiceDep,
):
    try:
        team = await team_service.get_team_by_id(task.team_id)
    except TeamDoesNotExistError:
        return RedirectResponse(
            request.url_for(TEAMS_LIST_PAGE_ROUTE_NAME),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        team_members = await team_service.get_team_members(team)

    comments = await comment_service.get_comments_for_task(task)

    if user.role == Role.MANAGER or user.role == Role.ADMIN or user.is_superuser:
        user_evaluation = await evaluation_service.get_user_evaluation_of_task(
            user, task
        )
    else:
        user_evaluation = None

    if task.assignee_id == user.id:
        filters = EvaluationsFilters(task_id=task.id)
        evaluations_of_user_task = (
            await evaluation_service.get_evaluations_of_user_tasks(user, filters)
        )
        avg_evaluation = await evaluation_service.get_avg_evaluation_of_user_tasks(
            user, filters
        )
    else:
        evaluations_of_user_task = None
        avg_evaluation = None

    return templates.TemplateResponse(
        request=request,
        name="tasks/detail.html",
        context={
            "title": f"Task {task.id}",
            "current_user": user,
            "task": task,
            "members": team_members,
            "comments": comments,
            "task_statuses": TaskStatus,
            "current_user_evaluation": user_evaluation,
            "evaluations_of_user_task": evaluations_of_user_task,
            "avg_evaluation": avg_evaluation,
        },
    )


@router.get("/{task_id}/edit", name=EDIT_TASK_PAGE_ROUTE_NAME)
async def task_edit_page(
    task: Annotated[
        Task,
        Depends(current_task(get_current_manager, task_team_member=True, author=True)),
    ],
    user: Annotated[User, Depends(get_current_manager)],
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="tasks/edit.html",
        context={
            "title": f"Edit task {task.id}",
            "current_user": user,
            "task": task,
            "task_statuses": TaskStatus,
        },
    )


@router.post("/{task_id}/edit", name=UPDATE_TASK_ROUTE_NAME)
async def update_task(
    user_timezone: Annotated[str, Form()],
    task: Annotated[
        Task,
        Depends(current_task(get_current_manager, task_team_member=True, author=True)),
    ],
    user: Annotated[User, Depends(get_current_manager)],
    task_service: TaskServiceDep,
    request: Request,
    description: Annotated[str | None, Form()] = None,
    deadline: Annotated[datetime | None, Form()] = None,
    task_status: Annotated[TaskStatus | None, Form()] = None,
):
    user_tz = pytz.timezone(user_timezone)

    try:
        update_data = TaskUpdate(
            description=description,
            deadline=user_tz.localize(deadline).astimezone(UTC)
            if deadline is not None
            else None,
            status=task_status,
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            request=request,
            name="tasks/edit.html",
            context={
                "title": f"Edit task {task.id}",
                "current_user": user,
                "task": task,
                "task_statuses": TaskStatus,
                "update_data": {
                    "description": description,
                    "deadline": deadline,
                    "status": task_status,
                },
                "error": e,
            },
        )

    await task_service.update_task(
        task, TaskUpdate(**update_data.model_dump(exclude_none=True))
    )

    return RedirectResponse(
        request.url_for(DETAIL_TASK_PAGE_ROUTE_NAME, task_id=task.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
