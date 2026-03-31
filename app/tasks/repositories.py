from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.tasks.models import Comment, Task
from app.tasks.schemas import CommentCreate, CommentUpdate, TaskCreate, TaskUpdate

if TYPE_CHECKING:
    from app.auth.models import User
    from app.teams.models import Team


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, task: TaskCreate, team: Team, author: User | None = None
    ) -> Task:
        """
        Create a new task

        :param task: data to create task with
        :param team: team to create task for
        :param author: user who is creating the task
        :return: created Task instance
        """
        db_task = Task(**task.model_dump(), author=author, team=team)
        self.session.add(db_task)

        return db_task

    async def get_by_id(self, task_id: int) -> Task | None:
        """
        Get task by id.

        :param task_id: id of task to get
        :return: Task instance or None if it was not found
        """
        return await self.session.get(Task, task_id)

    async def get_by_id_full(self, task_id: int) -> Task | None:
        """
        Get task by id with all relations.

        :param task_id: id of task to get
        :return: Task instance or None if it was not found
        """
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                joinedload(Task.author),
                joinedload(Task.assignee),
            )
        )
        return (await self.session.scalars(stmt)).one_or_none()

    async def get_tasks_assigned_to_user(self, user: User) -> list[Task]:
        """
        Get all tasks where a user is assignee

        :param user: user to get tasks for
        :return: list of tasks
        """
        stmt = (
            select(Task)
            .where(Task.assignee_id == user.id)
            .options(joinedload(Task.author), joinedload(Task.assignee))
        )
        return list(await self.session.scalars(stmt))

    async def get_tasks_created_by_user(self, user: User) -> list[Task]:
        """
        Get all tasks that were created by a user

        :param user: user to get tasks for
        :return: list of tasks
        """
        stmt = (
            select(Task)
            .where(Task.author_id == user.id)
            .options(joinedload(Task.author), joinedload(Task.assignee))
        )
        return list(await self.session.scalars(stmt))

    @classmethod
    async def update(cls, task: Task, update_data: TaskUpdate) -> Task:
        """
        Update a task.

        :param task: task to update
        :param update_data: data to update with
        :return: updated Task instance
        """
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)

        return task

    async def delete(self, task: Task) -> None:
        """
        Delete a task.

        :param task: task to delete
        :return: None
        """
        await self.session.delete(task)

    @classmethod
    async def assign_user_to_task(cls, task: Task, user: User) -> None:
        """
        Assign a user to a task.

        :param task: task to assign user to
        :param user: user to assign to a task
        :return: None
        """
        task.assignee = user


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: CommentCreate, user: User, task: Task) -> Comment:
        """
        Create a new comment.

        :param comment: data to create comment with
        :param user: user who is creating the comment
        :param task: task for which the comment is created
        :return: created Comment instance
        """
        db_comment = Comment(**comment.model_dump(), user=user, task=task)
        self.session.add(db_comment)

        return db_comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        """
        Get comment by id.

        :param comment_id: id of a comment to get
        :return: Comment instance or None if it was not found
        """
        return await self.session.get(
            Comment, comment_id, options=[joinedload(Comment.user)]
        )

    async def get_comments_for_task(self, task: Task) -> list[Comment]:
        """
        Get all comments for a task.

        :param task: task to get comments for
        :return: list of comments
        """
        stmt = (
            select(Comment)
            .where(Comment.task_id == task.id)
            .options(joinedload(Comment.user))
        )
        return list(await self.session.scalars(stmt))

    @classmethod
    async def update(cls, comment: Comment, update_data: CommentUpdate) -> Comment:
        """
        Update a comment.

        :param comment: comment to update
        :param update_data: data to update the comment with
        :return: updated Comment instance
        """
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(comment, key, value)

        return comment

    async def delete(self, comment: Comment) -> None:
        """
        Delete a comment.

        :param comment: comment to delete
        :return: None
        """
        await self.session.delete(comment)
