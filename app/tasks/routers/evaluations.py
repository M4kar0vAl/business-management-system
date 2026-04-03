from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app import responses
from app.auth.fastapi_users_instance import current_active_user, get_current_manager
from app.auth.models import User
from app.tasks.dependencies import (
    EvaluationServiceDep,
    evaluation_of_current_task,
    task_of_user_in_team,
)
from app.tasks.models import Evaluation, Task, TaskStatus
from app.tasks.schemas import (
    EvaluationCreate,
    EvaluationRead,
    EvaluationsPeriod,
    EvaluationUpdate,
)

EVALUATIONS_TAGS = ["Evaluations"]
user_evaluations_router = APIRouter(tags=EVALUATIONS_TAGS)
router = APIRouter(prefix="/{task_id}/evaluations", tags=EVALUATIONS_TAGS)

ROUTE_NAME_PREFIX = "evaluations"
EVALUATION_CREATE_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:create"
EVALUATION_UPDATE_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:update"
EVALUATION_DELETE_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:delete"
EVALUATION_GET_USER_EVALUATIONS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:of_user"
EVALUATION_GET_USER_AVG_EVALUATIONS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:avg_of_user"


@user_evaluations_router.get(
    "/my_evaluations",
    response_model=list[EvaluationRead],
    name=EVALUATION_GET_USER_EVALUATIONS_ROUTE_NAME,
)
async def get_user_evaluations(
    period: Annotated[EvaluationsPeriod, Query()],
    user: Annotated[User, Depends(current_active_user)],
    evaluations_service: EvaluationServiceDep,
):
    """
    Get evaluations of all tasks assigned to the current user.

    Active users only.
    """
    return await evaluations_service.get_evaluations_of_user_tasks(user, period)


@user_evaluations_router.get(
    "/my_evaluations/average",
    response_model=float,
    name=EVALUATION_GET_USER_AVG_EVALUATIONS_ROUTE_NAME,
)
async def get_avg_user_evaluation(
    period: Annotated[EvaluationsPeriod, Query()],
    user: Annotated[User, Depends(current_active_user)],
    evaluations_service: EvaluationServiceDep,
):
    """
    Get average evaluation of all tasks assigned to the current user.

    Active users only.
    """
    return await evaluations_service.get_avg_evaluation_of_user_tasks(user, period)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=EvaluationRead,
    responses={
        **responses.BAD_REQUEST_RESPONSE,
        **responses.ALREADY_EXISTS_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
    },
    name=EVALUATION_CREATE_ROUTE_NAME,
)
async def create_evaluation(
    evaluation: EvaluationCreate,
    user: Annotated[User, Depends(get_current_manager)],
    task: Annotated[
        Task, Depends(task_of_user_in_team(get_current_manager, status=TaskStatus.DONE))
    ],
    evaluation_service: EvaluationServiceDep,
):
    """
    Evaluate a task.

    In order to evaluate a task:
    - current user must be a member of a team where the task is created
    - current user should not have evaluated this task before
    - task with id `task_id` must exist
    - task status must be `done`

    Active manager or admin only.
    """
    created_evaluation = await evaluation_service.create_evaluation(
        evaluation, user, task
    )
    await evaluation_service.uow.flush()
    return created_evaluation


@router.patch(
    "/{evaluation_id}",
    response_model=EvaluationRead,
    responses={
        **responses.BAD_REQUEST_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
    },
    name=EVALUATION_UPDATE_ROUTE_NAME,
)
async def update_evaluation(
    evaluation: Annotated[
        Evaluation,
        Depends(
            evaluation_of_current_task(
                get_current_manager,
                task_of_user_in_team(get_current_manager, status=TaskStatus.DONE),
                author=True,
            )
        ),
    ],
    update_data: EvaluationUpdate,
    evaluation_service: EvaluationServiceDep,
):
    """
    Update evaluation of a task.

    In order to update an evaluation:
    - current user must be a member of a team where the task is created
    - current user must be the author of the evaluation
    - evaluation with id `evaluation_id` must exist
    - evaluation should belong to the task
    - task with id `task_id` must exist
    - task status must be `done`

    Active manager or admin only.
    """
    updated_evaluation = await evaluation_service.update_evaluation(
        evaluation, update_data
    )
    await evaluation_service.uow.flush()
    return updated_evaluation


@router.delete(
    "/{evaluation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.BAD_REQUEST_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
    },
    name=EVALUATION_DELETE_ROUTE_NAME,
)
async def delete_evaluation(
    evaluation: Annotated[
        Evaluation,
        Depends(
            evaluation_of_current_task(
                get_current_manager,
                task_of_user_in_team(get_current_manager),
                author=True,
            )
        ),
    ],
    evaluation_service: EvaluationServiceDep,
):
    """
    Delete evaluation of a task.

    In order to delete an evaluation:
    - current user must be a member of a team where the task is created
    - current user must be the author of the evaluation
    - evaluation with id `evaluation_id` must exist
    - evaluation should belong to the task
    - task with id `task_id` must exist

    Active manager or admin only.
    """
    await evaluation_service.delete_evaluation(evaluation)
