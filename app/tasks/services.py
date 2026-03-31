from typing import TYPE_CHECKING

from app.auth.types import UserIdType
from app.auth.user_manager import UserManager
from app.tasks.exceptions import (
    CommentDoesNotExistError,
    TaskAlreadyAssignedError,
    TaskDoesNotExistError,
    UserIsNotTaskAssigneeError,
)
from app.tasks.repositories import CommentRepository, TaskRepository
from app.tasks.schemas import CommentCreate, CommentUpdate, TaskCreate, TaskUpdate
from app.teams.exceptions import TeamDoesNotExistError, UserDoesNotBelongToTeamError
from app.teams.repositories import TeamRepository
from app.uow import UnitOfWork

if TYPE_CHECKING:
    from app.auth.models import User
    from app.tasks.models import Comment, Task, TaskStatus


class TaskService:
    def __init__(self, uow: UnitOfWork, user_manager: UserManager):
        self.uow = uow
        self.task_repo = TaskRepository(uow.session)
        self.team_repo = TeamRepository(uow.session)
        self.user_manager = user_manager

    async def create_task(self, task: TaskCreate, author: User) -> Task:
        """
        Create a new task.

        :param task: data to create task with
        :param author: user who is creating the task
        :return: Task instance
        :raises UserDoesNotBelongToTeamError: if author is not a member of a team with id `team_id`
        :raises TeamDoesNotExistError: if the team does not exist
        """
        team = await self.team_repo.get_by_id(task.team_id)

        if not team:
            raise TeamDoesNotExistError(task.team_id)

        self._check_user_belongs_to_team(author, task.team_id)

        return await self.task_repo.create(task, author=author, team=team)

    async def get_task_by_id(self, task_id: int, full: bool = False) -> Task:
        """
        Get task by id.

        :param task_id: id of a task to get
        :param full: a boolean indicating whether to query a task with all its relations or not
        :return: Task instance
        :raises TaskDoesNotExistError: if Task with the given id does not exist
        """
        if full:
            task = await self.task_repo.get_by_id_full(task_id)
        else:
            task = await self.task_repo.get_by_id(task_id)

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

    async def assign_user_to_task(self, task: Task, assignee_id: UserIdType) -> None:
        """
        Assign user to task.

        :param task: task to assign user to
        :param assignee_id: id of user to assign to the task
        :return: None
        :raises TaskAlreadyAssignedError: if the task is already assigned to another user
        :raises UserNotExists: if the user with the given id does not exist
        :raises UserDoesNotBelongToTeamError: if assigner or assignee is not a member of a team where the task is created
        """
        if task.assignee_id is not None:
            raise TaskAlreadyAssignedError(task)

        assignee = await self.user_manager.get(assignee_id)
        self._check_user_belongs_to_team(assignee, task.team_id)

        await self.task_repo.assign_user_to_task(task, assignee)

    async def update_task(
        self,
        task: Task,
        update_data: TaskUpdate,
    ) -> Task:
        """
        Update a task.

        :param task: task to update
        :param update_data: data to update the task with
        :return: Task instance
        """
        return await self.task_repo.update(task, update_data)

    async def delete_task(self, task: Task) -> None:
        """
        Delete a task.

        :param task: task to delete
        :param user: user who is deleting task
        :return: None
        """
        await self.task_repo.delete(task)

    async def update_task_status(
        self, task: Task, status: TaskStatus, user: User
    ) -> Task:
        """
        Update task status.

        :param task: task to update
        :param status: status to update to
        :param user: user performing the update
        :return: updated task
        :raises UserIsNotTaskAssigneeError: if user is not assigned to the task
        """
        if not task.assignee_id == user.id:
            raise UserIsNotTaskAssigneeError(task, user.id)

        return await self.task_repo.update(task, TaskUpdate(status=status))

    @classmethod
    def _check_user_belongs_to_team(cls, user: User, team_id: int) -> None:
        if user.team_id != team_id:
            raise UserDoesNotBelongToTeamError(user, team_id)


class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.comment_repo = CommentRepository(uow.session)

    async def create_comment(
        self, comment: CommentCreate, user: User, task: Task
    ) -> Comment:
        """
        Create a new comment.

        :param comment: data to create comment with
        :param user: user who is creating the comment
        :param task: task to comment
        :return: created Comment instance
        """
        return await self.comment_repo.create(comment, user, task)

    async def get_comment_by_id(self, comment_id: int) -> Comment:
        """
        Get comment by id.

        :param comment_id: id of a comment to get
        :return: Comment instance
        :raises CommentDoesNotExistError: if the comment with the given id does not exist
        """
        comment = await self.comment_repo.get_by_id(comment_id)

        if not comment:
            raise CommentDoesNotExistError(comment_id)

        return comment

    async def update_comment(
        self,
        comment: Comment,
        update_data: CommentUpdate,
    ) -> Comment:
        """
        Update a comment.

        :param comment: comment to update
        :param update_data: data to update the comment with
        :return: updated Comment instance
        """
        return await self.comment_repo.update(comment, update_data)

    async def delete_comment(self, comment: Comment) -> None:
        """
        Delete a comment.

        :param comment: comment to delete
        :return: None
        """
        await self.comment_repo.delete(comment)
