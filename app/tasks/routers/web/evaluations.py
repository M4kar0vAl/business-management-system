from contextlib import suppress
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.auth.fastapi_users_instance import get_current_manager
from app.auth.models import User
from app.tasks.dependencies import EvaluationServiceDep, current_task
from app.tasks.exceptions import EvaluationAlreadyExistsError
from app.tasks.models import Task, TaskStatus
from app.tasks.routers.web.tasks import DETAIL_TASK_PAGE_ROUTE_NAME
from app.tasks.schemas import EvaluationCreate

router = APIRouter(prefix="/{task_id}/evaluations")

EVALUATION_CREATE_ROUTE_NAME = "create_evaluation"


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
