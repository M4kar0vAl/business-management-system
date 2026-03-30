from typing import Annotated

from fastapi import APIRouter, Depends, status

from app import responses
from app.auth.fastapi_users_instance import current_active_user, get_current_manager
from app.auth.models import User
from app.auth.types import UserIdType
from app.tasks.dependencies import TaskServiceDep
from app.tasks.schemas import TaskCreate, TaskRead
from app.tasks.schemas.tasks import TaskReadFull, TaskUpdate

router = APIRouter()

ROUTE_NAME_PREFIX = "tasks"
TASK_CREATE_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:create"
GET_ASSIGNED_TASKS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_assigned"
GET_CREATED_TASKS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_created"
GET_TASK_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:retrieve"
UPDATE_TASK_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:update"
DELETE_TASK_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:delete"
ASSIGN_USER_TO_TASK_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:assign_user"


# TODO move this one to teams router probably
@router.post(
    "/teams/{team_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskRead,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=TASK_CREATE_ROUTE_NAME,
)
async def create_task(
    task: TaskCreate,
    team_id: int,
    author: Annotated[User, Depends(get_current_manager)],
    task_service: TaskServiceDep,
):
    """
    Create a new task.

    In order to create task:
    - current user must be a member of a team with id `team_id`
    - current user must have at least `"manager"` role
    - team with id `team_id` must exist

    Active manager or admin only.
    """
    created_task = await task_service.create_task(task, team_id, author)
    await task_service.uow.flush()
    return created_task


@router.get(
    "/assigned", response_model=list[TaskRead], name=GET_ASSIGNED_TASKS_ROUTE_NAME
)
async def get_tasks_assigned(
    user: Annotated[User, Depends(current_active_user)], task_service: TaskServiceDep
):
    """
    Get all tasks assigned to a current user.

    Active user only.
    """
    return await task_service.get_tasks_assigned_to_user(user)


@router.get(
    "/created", response_model=list[TaskRead], name=GET_CREATED_TASKS_ROUTE_NAME
)
async def get_tasks_created(
    user: Annotated[User, Depends(get_current_manager)], task_service: TaskServiceDep
):
    """
    Get all tasks created by a current user.

    Active manager or admin only.
    """
    return await task_service.get_tasks_created_by_user(user)


@router.get(
    "/{task_id}",
    response_model=TaskReadFull,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=GET_TASK_ROUTE_NAME,
)
async def get_task_by_id(
    task_id: int,
    user: Annotated[User, Depends(current_active_user)],
    task_service: TaskServiceDep,
):
    """
    Get a task by id.

    Active user only.
    """
    return await task_service.get_task_by_id(task_id, user)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=UPDATE_TASK_ROUTE_NAME,
)
async def update_task(
    task_id: int,
    update_data: TaskUpdate,
    user: Annotated[User, Depends(get_current_manager)],
    task_service: TaskServiceDep,
):
    """
    Update a task.

    In order to update a task:
    - current user must be a member of a team where the task is created
    - current user must have at least `"manager"` role
    - task with id `task_id` must exist

    Active manager or admin only.
    """
    return await task_service.update_task(task_id, update_data, user)


@router.delete(
    "/{task_id}",
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=DELETE_TASK_ROUTE_NAME,
)
async def delete_task(
    task_id: int,
    user: Annotated[User, Depends(get_current_manager)],
    task_service: TaskServiceDep,
):
    """
    Delete a task.

    In order to delete a task:
    - current user must be a member of a team where the task is created
    - current user must have at least `"manager"` role
    - task with id `task_id` must exist

    Active manager or admin only.
    """
    await task_service.delete_task(task_id, user)


@router.post(
    "/{task_id}/assignees/{assignee_id}",
    responses={
        **responses.SUCCESS_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.BAD_REQUEST_RESPONSE,
    },
    name=ASSIGN_USER_TO_TASK_ROUTE_NAME,
)
async def assign_user_to_task(
    task_id: int,
    assignee_id: UserIdType,
    assigner: Annotated[User, Depends(get_current_manager)],
    task_service: TaskServiceDep,
):
    """
    Assign a user to a task.

    In order to assign user to a task:
    - current user must be a member of a team where the task is created
    - assignee must be a member of a team where the task is created
    - current user must have at least `"manager"` role
    - task with id `task_id` must exist
    - task must not be assigned to any other user

    Active manager or admin only.
    """
    await task_service.assign_user_to_task(task_id, assignee_id, assigner)

    return {"detail": "User assigned to the task successfully"}
