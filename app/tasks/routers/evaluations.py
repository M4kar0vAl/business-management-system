from typing import Annotated

from fastapi import APIRouter, Depends, status

from app import responses
from app.auth.fastapi_users_instance import get_current_manager
from app.auth.models import User
from app.tasks.dependencies import (
    EvaluationServiceDep,
    evaluation_of_current_task,
    task_of_user_in_team,
)
from app.tasks.models import Evaluation, Task, TaskStatus
from app.tasks.schemas import EvaluationCreate, EvaluationRead, EvaluationUpdate

router = APIRouter(prefix="/{task_id}/evaluations", tags=["Evaluations"])


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
    return await evaluation_service.create_evaluation(evaluation, user, task)


@router.patch(
    "/{evaluation_id}",
    response_model=EvaluationRead,
    responses={
        **responses.BAD_REQUEST_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
    },
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
    return await evaluation_service.update_evaluation(evaluation, update_data)


@router.delete(
    "/{evaluation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.BAD_REQUEST_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
    },
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
