from typing import TYPE_CHECKING

from app.auth.types import UserIdType
from app.auth.user_manager import UserManager
from app.tasks.exceptions import (
    CommentDoesNotBelongToUser,
    CommentDoesNotExistError,
    TaskAlreadyAssignedError,
    TaskDoesNotExistError,
)
from app.tasks.repositories import CommentRepository, TaskRepository
from app.tasks.schemas import CommentCreate, CommentUpdate, TaskCreate, TaskUpdate
from app.teams.exceptions import TeamDoesNotExistError, UserDoesNotBelongToTeamError
from app.teams.repositories import TeamRepository
from app.uow import UnitOfWork

if TYPE_CHECKING:
    from app.auth.models import User
    from app.tasks.models import Comment, Task


class TaskService:
    def __init__(self, uow: UnitOfWork, user_manager: UserManager):
        self.uow = uow
        self.task_repo = TaskRepository(uow.session)
        self.team_repo = TeamRepository(uow.session)
        self.user_manager = user_manager

    async def create_task(self, task: TaskCreate, team_id: int, author: User) -> Task:
        """
        Create a new task.

        :param task: data to create task with
        :param team_id: id of a team to create task for
        :param author: user who is creating the task
        :return: Task instance
        :raises UserDoesNotBelongToTeamError: if author is not a member of a team with id `team_id`
        :raises TeamDoesNotExistError: if the team does not exist
        """
        if author.team_id != team_id:
            raise UserDoesNotBelongToTeamError(author, team_id)

        team = await self.team_repo.get_by_id(team_id)

        if not team:
            raise TeamDoesNotExistError(team_id)

        return await self.task_repo.create(task, author=author, team=team)

    async def get_task_by_id(self, task_id: int) -> Task:
        """
        Get task by id.

        :param task_id: id of a task to get
        :return: Task instance
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        """
        task = await self.task_repo.get_by_id_full(task_id)

        if not task:
            raise TaskDoesNotExistError(task_id)

        return task

    async def get_tasks_assigned_to_user(self, user: User) -> list[Task]:
        """
        Get tasks assigned to a user.

        :param user: user for whom to get assigned tasks
        :return: list of tasks
        """
        return await self.task_repo.get_tasks_assigned_to_user(user)

    async def get_tasks_created_by_user(self, user: User) -> list[Task]:
        """
        Get tasks created by a user.

        :param user: user for whom to get created tasks
        :return: list of tasks
        """
        return await self.task_repo.get_tasks_created_by_user(user)

    async def assign_user_to_task(self, task_id: int, assignee_id: UserIdType) -> None:
        """
        Assign user to task.

        :param task_id: id of a task to assign user to
        :param assignee_id: id of user to assign to the task
        :return: None
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        :raises TaskAlreadyAssignedError: if the task is already assigned to another user
        :raises UserNotExists: if the user with the given id does not exist
        """
        task = await self._get_task_by_id(task_id)

        if task.assignee_id is not None:
            raise TaskAlreadyAssignedError(task)

        assignee = await self.user_manager.get(assignee_id)

        await self.task_repo.assign_user_to_task(task, assignee)

    async def update_task(self, task_id: int, update_data: TaskUpdate) -> Task:
        """
        Update a task.

        :param task_id: id of a task to update
        :param update_data: data to update the task with
        :return: Task instance
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        """
        task = await self._get_task_by_id(task_id)

        return await self.task_repo.update(task, update_data)

    async def delete_task(self, task_id: int) -> None:
        """
        Delete a task.

        :param task_id: id of a task to delete
        :return: None
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        """
        task = await self._get_task_by_id(task_id)

        await self.task_repo.delete(task)

    async def _get_task_by_id(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskDoesNotExistError(task_id)

        return task


class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.comment_repo = CommentRepository(uow.session)
        self.task_repo = TaskRepository(uow.session)

    async def create_comment(
        self, comment: CommentCreate, user: User, task_id: int
    ) -> Comment:
        """
        Create a new comment.

        :param comment: data to create comment with
        :param user: user who is creating the comment
        :param task_id: id of a task to comment
        :return: created Comment instance
        :raises TaskDoesNotExistError: if task with the given id does not exist
        :raises UserDoesNotBelongToTeamError: if the user is not a member of the team where the task is created
        """
        task = await self._get_task_by_id(task_id)
        self._check_user_belongs_to_task_team(user, task)

        return await self.comment_repo.create(comment, user, task)

    async def update_comment(
        self, comment_id: int, update_data: CommentUpdate, user: User, task_id: int
    ) -> Comment:
        """
        Update a comment.

        :param comment_id: id of a comment to update
        :param update_data: data to update the comment with
        :param user: user who is updating the comment
        :param task_id: id of the task for which to update the comment
        :return: updated Comment instance
        :raises CommentDoesNotExistError: if Comment with the given id does not exist
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        :raises CommentDoesNotBelongToUser: if the user is not the one who created the comment
        :raises UserDoesNotBelongToTeamError: if the user is not a member of the team where the task is created
        """
        comment = await self._get_comment_by_id(comment_id)
        self._check_comment_belongs_to_user(comment, user)

        task = await self._get_task_by_id(task_id)
        self._check_user_belongs_to_task_team(user, task)

        return await self.comment_repo.update(comment, update_data)

    async def delete_comment(self, comment_id: int, user: User, task_id: int) -> None:
        """
        Delete a comment.

        :param comment_id: id of a comment to delete
        :param user: user who is deleting the comment
        :param task_id: id of the task for which to delete the comment
        :return: None
        :raises CommentDoesNotExistError: if Comment with the given id does not exist
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        :raises CommentDoesNotBelongToUser: if the user is not the one who created the comment
        :raises UserDoesNotBelongToTeamError: if the user is not a member of the team where the task is created
        """
        comment = await self._get_comment_by_id(comment_id)
        self._check_comment_belongs_to_user(comment, user)

        task = await self._get_task_by_id(task_id)
        self._check_user_belongs_to_task_team(user, task)

        await self.comment_repo.delete(comment)

    async def _get_comment_by_id(self, comment_id: int) -> Comment:
        comment = await self.comment_repo.get_by_id(comment_id)

        if not comment:
            raise CommentDoesNotExistError(comment_id)

        return comment

    async def _get_task_by_id(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise TaskDoesNotExistError(task_id)

        return task

    @classmethod
    def _check_comment_belongs_to_user(cls, comment: Comment, user: User) -> None:
        if comment.user_id != user.id:
            raise CommentDoesNotBelongToUser(comment.id, user.id)

    @classmethod
    def _check_user_belongs_to_task_team(cls, user: User, task: Task) -> None:
        if user.team_id != task.team_id:
            raise UserDoesNotBelongToTeamError(user, task.team_id)
