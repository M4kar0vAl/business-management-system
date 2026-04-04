from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.models import User
from app.tasks.models import Evaluation, Task
from app.tasks.schemas import EvaluationCreate, EvaluationsFilters, EvaluationUpdate


class EvaluationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, evaluation: EvaluationCreate, user: User, task: Task
    ) -> Evaluation:
        """
        Create a new evaluation.

        :param evaluation: data to create evaluation with
        :param user: user who is creating the evaluation
        :param task: task for which the evaluation is created
        :return: created Evaluation instance
        """
        db_evaluation = Evaluation(**evaluation.model_dump(), author=user, task=task)
        self.session.add(db_evaluation)

        return db_evaluation

    async def get_by_id(self, evaluation_id: int) -> Evaluation | None:
        """
        Get evaluation by id.

        :param evaluation_id: id of an evaluation to get
        :return: Evaluation instance or None if it was not found
        """
        stmt = (
            select(Evaluation)
            .where(Evaluation.id == evaluation_id)
            .options(joinedload(Evaluation.author))
        )
        return (await self.session.scalars(stmt)).one_or_none()

    async def get_by_user_and_task(self, user: User, task: Task) -> Evaluation | None:
        """
        Get user evaluation of the task.

        :param user: user who is the author of the evaluation
        :param task: task for which to get the evaluation
        :return: Evaluation instance or None if it was not found
        """
        stmt = select(Evaluation).where(
            Evaluation.author_id == user.id, Evaluation.task_id == task.id
        )
        return (await self.session.scalars(stmt)).one_or_none()

    async def get_evaluations_of_user_tasks(
        self, user: User, filters: EvaluationsFilters
    ) -> list[Evaluation]:
        """
        Get evaluations of all tasks of the user where they are the assignee.

        :param user: user to get evaluations for
        :param filters: period within which to get the evaluations
        :return: list of evaluations
        """
        filters_list = self._get_filters(filters)

        stmt = (
            select(Evaluation)
            .join(Task, Evaluation.task_id == Task.id)
            .where(Task.assignee_id == user.id, *filters_list)
        )

        return list(await self.session.scalars(stmt))

    async def get_avg_evaluation_of_user_tasks(
        self, user: User, filters: EvaluationsFilters
    ) -> float:
        """
        Get average value of evaluations of tasks of the user where they are the assignee.

        :param user: user to get average evaluation for
        :param filters: filters to apply
        :return: average evaluation for the given period
        """
        filters_list = self._get_filters(filters)

        stmt = (
            select(func.coalesce(func.avg(Evaluation.value), 0.0))
            .join(Task, Evaluation.task_id == Task.id)
            .where(Task.assignee_id == user.id, *filters_list)
        )

        return await self.session.scalar(stmt)

    @classmethod
    async def update(
        cls, evaluation: Evaluation, update_data: EvaluationUpdate
    ) -> Evaluation:
        """
        Update an evaluation.

        :param evaluation: evaluation to update
        :param update_data: data to update the evaluation with
        :return: updated Evaluation instance
        """
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(evaluation, key, value)

        return evaluation

    async def delete(self, evaluation: Evaluation) -> None:
        """
        Delete an evaluation.

        :param evaluation: evaluation to delete
        :return: None
        """
        await self.session.delete(evaluation)

    @classmethod
    def _get_filters(cls, filters: EvaluationsFilters):
        filters_list = []

        period_start = filters.start
        if period_start is not None:
            start_datetime = datetime(
                period_start.year, period_start.month, period_start.day, tzinfo=UTC
            )
            filters_list.append(Evaluation.created_at >= start_datetime)

        period_end = filters.end
        if period_end is not None:
            end_datetime_exclusive = datetime(
                period_end.year, period_end.month, period_end.day, tzinfo=UTC
            ) + timedelta(days=1)
            filters_list.append(Evaluation.created_at < end_datetime_exclusive)

        task_id = filters.task_id
        if task_id is not None:
            filters_list.append(Evaluation.task_id == task_id)

        return filters_list
