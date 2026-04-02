from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Path

from app.auth.dependencies import get_user_manager
from app.auth.models import User
from app.auth.user_manager import UserManager
from app.dependencies import UOWDep
from app.http_exceptions import ForbiddenError
from app.tasks.exceptions import (
    CommentDoesNotBelongToUser,
)
from app.tasks.models import Comment
from app.tasks.services import CommentService, TaskService
from app.tasks.services import CommentService, EvaluationService, TaskService
from app.teams.exceptions import UserDoesNotBelongToTeamError

if TYPE_CHECKING:
    from app.tasks.models import Task


async def get_task_service(
    uow: UOWDep, user_manager: Annotated[UserManager, Depends(get_user_manager)]
):
    yield TaskService(uow, user_manager)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


async def get_comments_service(uow: UOWDep):
    yield CommentService(uow)


CommentServiceDep = Annotated[CommentService, Depends(get_comments_service)]


def current_task(full: bool = False):
async def get_evaluations_service(uow: UOWDep):
    yield EvaluationService(uow)


EvaluationServiceDep = Annotated[EvaluationService, Depends(get_evaluations_service)]


    """
    Dependency factory to get task from `task_id` path parameter.

    :param full: boolean indicating whether to get task with all its relations
    :return: dependency for getting current task
    :raises TaskDoesNotExistError: if the task with the given id does not exist
    """

    async def _current_task(
        task_id: Annotated[int, Path()], task_service: TaskServiceDep
    ):
        return await task_service.get_task_by_id(task_id, full=full)

    return _current_task


def task_of_user_in_team(
    user_dep: Callable[..., User | Awaitable[User]],
    full: bool = False,
    author: bool = False,
):
    """
    Dependency factory to get task from `task_id` path parameter.

    Dependency will perform validation that user belongs to team where the task is created.

    :param user_dep: dependency for getting the user performing the action
    :param full: boolean indicating whether to get task with all its relations
    :param author: boolean indicating whether to check that user is the one who created the task
    :return: dependency for getting the current task
    :raises TaskDoesNotExistError: if the task with the given id does not exist
    :raises UserDoesNotBelongToTeamError: if the user does not belong to the team where the task is created
    :raises ForbiddenError: if author is True and the user is not an author of the task
    """

    async def _task_of_user_in_team(
        task: Annotated[Task, Depends(current_task(full=full))],
        user: Annotated[User, Depends(user_dep)],
    ):
        if user.team_id != task.team_id:
            raise UserDoesNotBelongToTeamError(user, task.team_id)

        if author and task.author_id != user.id:
            raise ForbiddenError()

        return task

    return _task_of_user_in_team


async def current_comment(
    comment_id: Annotated[int, Path()], comment_service: CommentServiceDep
):
    """
    Dependency to get comment from `comment_id` path parameter.

    :return: Comment instance
    :raises CommentDoesNotExistError: if the comment with the given id does not exist
    """
    return await comment_service.get_comment_by_id(comment_id)


CurrentCommentDep = Annotated[Comment, Depends(current_comment)]


def comment_of_current_user(user_dep: Callable[..., User | Awaitable[User]]):
    """
    Dependency factory to get comment from `comment_id` path parameter.

    Dependency will perform validation that user is the comment author.

    :param user_dep: dependency for getting the user performing the action
    :return: dependency for getting the current comment
    :raises CommentDoesNotExistError: if the comment with the given id does not exist
    :raises CommentDoesNotBelongToUser: if the user is not an author of the comment
    """

    async def _comment_of_current_user(
        comment: CurrentCommentDep, user: Annotated[User, Depends(user_dep)]
    ):
        if comment.user_id != user.id:
            raise CommentDoesNotBelongToUser(comment.id, user.id)

        return comment

    return _comment_of_current_user
