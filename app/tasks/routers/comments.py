from typing import Annotated

from fastapi import APIRouter, Depends, status

from app import responses
from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.tasks.dependencies import CommentServiceDep
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
    task_id: int,
    user: Annotated[User, Depends(current_active_user)],
    comment_service: CommentServiceDep,
):
    """
    Create a new comment.

    To create a comment one must be a member of the team where the task is created.

    Active users only.
    """
    created_comment = await comment_service.create_comment(comment, user, task_id)
    await comment_service.uow.flush()
    return created_comment


@router.patch(
    "/{comment_id}",
    response_model=CommentRead,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=UPDATE_COMMENT_ROUTE_NAME,
)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    task_id: int,
    user: Annotated[User, Depends(current_active_user)],
    comment_service: CommentServiceDep,
):
    """
    Update a comment.

    To update a comment one must be:
    - a member of the team where the task is created
    - the creator of the comment

    Active users only.
    """
    updated_comment = await comment_service.update_comment(
        comment_id, comment, user, task_id
    )
    await comment_service.uow.flush()
    return updated_comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=DELETE_COMMENT_ROUTE_NAME,
)
async def delete_comment(
    comment_id: int,
    task_id: int,
    user: Annotated[User, Depends(current_active_user)],
    comment_service: CommentServiceDep,
):
    """
    Delete a comment.

    To delete a comment one must be:
    - a member of the team where the task is created
    - the creator of the comment

    Active users only.
    """
    await comment_service.delete_comment(comment_id, user, task_id)
