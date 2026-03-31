from typing import Annotated

from fastapi import APIRouter, Depends, status

from app import responses
from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.tasks.dependencies import (
    CommentServiceDep,
    comment_of_current_user,
    task_of_user_in_team,
)
from app.tasks.models import Comment, Task
from app.tasks.schemas import CommentCreate, CommentRead, CommentUpdate

router = APIRouter(prefix="/{task_id}/comments", tags=["Comments"])

ROUTE_NAME_PREFIX = "tasks_comments"
CREATE_COMMENT_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:create"
UPDATE_COMMENT_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:update"
DELETE_COMMENT_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:delete"


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentRead,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=CREATE_COMMENT_ROUTE_NAME,
)
async def create_comment(
    comment: CommentCreate,
    task: Annotated[Task, Depends(task_of_user_in_team(current_active_user))],
    user: Annotated[User, Depends(current_active_user)],
    comment_service: CommentServiceDep,
):
    """
    Create a new comment.

    To create a comment one must be a member of the team where the task is created.

    Active users only.
    """
    created_comment = await comment_service.create_comment(comment, user, task)
    await comment_service.uow.flush()
    return created_comment


@router.patch(
    "/{comment_id}",
    response_model=CommentRead,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    dependencies=[Depends(task_of_user_in_team(current_active_user))],
    name=UPDATE_COMMENT_ROUTE_NAME,
)
async def update_comment(
    comment: Annotated[Comment, Depends(comment_of_current_user(current_active_user))],
    comment_update: CommentUpdate,
    comment_service: CommentServiceDep,
):
    """
    Update a comment.

    To update a comment one must be:
    - a member of the team where the task is created
    - the creator of the comment

    Active users only.
    """
    updated_comment = await comment_service.update_comment(comment, comment_update)
    await comment_service.uow.flush()
    return updated_comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    dependencies=[Depends(task_of_user_in_team(current_active_user))],
    name=DELETE_COMMENT_ROUTE_NAME,
)
async def delete_comment(
    comment: Annotated[Comment, Depends(comment_of_current_user(current_active_user))],
    comment_service: CommentServiceDep,
):
    """
    Delete a comment.

    To delete a comment one must be:
    - a member of the team where the task is created
    - the creator of the comment

    Active users only.
    """
    await comment_service.delete_comment(comment)
