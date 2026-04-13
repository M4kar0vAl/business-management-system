from datetime import UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.models import User
from app.tasks.models import Task
from app.tasks.schemas import TaskCreate, TaskUpdate
from app.tasks.schemas.tasks import TasksCalendarFilters
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

    async def get_calendar_tasks(self, filters: TasksCalendarFilters) -> list[Task]:
        """
        Get tasks to display in calendar.

        :param filters: filters to apply, including calendar period.
        :return: list of tasks
        """
        filters_list = self._get_calendar_filters(filters)
        stmt = select(Task).where(*filters_list)

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

    @classmethod
    def _get_calendar_filters(cls, filters: TasksCalendarFilters):
        filters_list = [
            Task.deadline >= filters.start.astimezone(UTC),
            Task.deadline <= filters.end.astimezone(UTC),
        ]

        if (team_id := filters.team_id) is not None:
            filters_list.append(Task.team_id == team_id)

        if (assignee_id := filters.assignee_id) is not None:
            filters_list.append(Task.assignee_id == assignee_id)

        return filters_list
