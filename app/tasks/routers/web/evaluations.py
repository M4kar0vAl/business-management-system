from contextlib import suppress
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.auth.fastapi_users_instance import get_current_manager
from app.auth.models import User
from app.tasks.dependencies import (
    EvaluationServiceDep,
    current_task,
    evaluation_of_current_task,
)
from app.tasks.exceptions import EvaluationAlreadyExistsError
from app.tasks.models import Evaluation, Task, TaskStatus
from app.tasks.routers.web.tasks import DETAIL_TASK_PAGE_ROUTE_NAME
from app.tasks.schemas import EvaluationCreate, EvaluationUpdate

router = APIRouter(prefix="/{task_id}/evaluations")

EVALUATION_CREATE_ROUTE_NAME = "create_evaluation"
EVALUATION_UPDATE_ROUTE_NAME = "update_evaluation"
EVALUATION_DELETE_ROUTE_NAME = "delete_evaluation"


@router.post("/", name=EVALUATION_CREATE_ROUTE_NAME)
async def create_evaluation(
    task: Annotated[
        Task,
        Depends(
            current_task(
                get_current_manager, task_team_member=True, status=TaskStatus.DONE
            )
        ),
    ],
    user: Annotated[User, Depends(get_current_manager)],
    evaluation: Annotated[EvaluationCreate, Form()],
    evaluation_service: EvaluationServiceDep,
    request: Request,
):
    with suppress(EvaluationAlreadyExistsError):
        await evaluation_service.create_evaluation(evaluation, user, task)

    return RedirectResponse(
        request.url_for(DETAIL_TASK_PAGE_ROUTE_NAME, task_id=task.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{evaluation_id}/update", name=EVALUATION_UPDATE_ROUTE_NAME)
async def update_evaluation(
    task_id: int,
    evaluation: Annotated[
        Evaluation,
        Depends(
            evaluation_of_current_task(
                get_current_manager,
                current_task(
                    get_current_manager, task_team_member=True, status=TaskStatus.DONE
                ),
                author=True,
            )
        ),
    ],
    update_data: Annotated[EvaluationUpdate, Form()],
    evaluation_service: EvaluationServiceDep,
    request: Request,
):
    await evaluation_service.update_evaluation(evaluation, update_data)

    return RedirectResponse(
        request.url_for(DETAIL_TASK_PAGE_ROUTE_NAME, task_id=task_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{evaluation_id}/delete", name=EVALUATION_DELETE_ROUTE_NAME)
async def delete_evaluation(
    task_id: int,
    evaluation: Annotated[
        Evaluation,
        Depends(
            evaluation_of_current_task(
                get_current_manager,
                current_task(
                    get_current_manager,
                    task_team_member=True,
                ),
                author=True,
            )
        ),
    ],
    evaluation_service: EvaluationServiceDep,
    request: Request,
):
    await evaluation_service.delete_evaluation(evaluation)

    return RedirectResponse(
        request.url_for(DETAIL_TASK_PAGE_ROUTE_NAME, task_id=task_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
