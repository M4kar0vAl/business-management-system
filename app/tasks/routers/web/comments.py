from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse

from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.tasks.dependencies import CommentServiceDep, current_comment, current_task
from app.tasks.models import Comment, Task
from app.tasks.routers.web.tasks import DETAIL_TASK_PAGE_ROUTE_NAME
from app.tasks.schemas import CommentCreate

router = APIRouter(prefix="/{task_id}/comments")

COMMENT_CREATE_ROUTE_NAME = "create_comment"
COMMENT_DELETE_ROUTE_NAME = "delete_comment"


@router.post("/", name=COMMENT_CREATE_ROUTE_NAME)
async def create_comment(
    create_data: Annotated[CommentCreate, Form()],
    user: Annotated[User, Depends(current_active_user)],
    task: Annotated[
        Task, Depends(current_task(current_active_user, task_team_member=True))
    ],
    comment_service: CommentServiceDep,
    request: Request,
):
    await comment_service.create_comment(create_data, user, task)

    return RedirectResponse(
        request.url_for(DETAIL_TASK_PAGE_ROUTE_NAME, task_id=task.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{comment_id}/delete", name=COMMENT_DELETE_ROUTE_NAME)
async def delete_comment(
    task: Annotated[
        Task, Depends(current_task(current_active_user, task_team_member=True))
    ],
    comment: Annotated[
        Comment, Depends(current_comment(current_active_user, author=True))
    ],
    comment_service: CommentServiceDep,
    request: Request,
):
    await comment_service.delete_comment(comment)

    return RedirectResponse(
        request.url_for(DETAIL_TASK_PAGE_ROUTE_NAME, task_id=task.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
