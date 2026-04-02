from typing import TYPE_CHECKING

from app.tasks.exceptions import (
    EvaluationAlreadyExistsError,
    EvaluationDoesNotBelongToTaskError,
    EvaluationDoesNotExistError,
    InvalidTaskStatusError,
)
from app.tasks.repositories import EvaluationRepository
from app.tasks.schemas import EvaluationCreate, EvaluationsPeriod, EvaluationUpdate
from app.uow import UnitOfWork

if TYPE_CHECKING:
    from app.auth.models import User
    from app.tasks.models import Evaluation, Task, TaskStatus


class EvaluationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.evaluation_repo = EvaluationRepository(uow.session)

    async def create_evaluation(
        self, evaluation: EvaluationCreate, user: User, task: Task
    ) -> Evaluation:
        """
        Create a new evaluation.

        :param evaluation: data to create evaluation with
        :param user: user who is creating the evaluation
        :param task: task to evaluate
        :return: created Evaluation instance
        :raises EvaluationAlreadyExistsError: if the user has already evaluated the task
        :raises InvalidTaskStatusError: if the task does not have `TaskStatus.DONE` status
        """
        if task.status != TaskStatus.DONE:
            raise InvalidTaskStatusError(task, TaskStatus.DONE)

        if self.evaluation_repo.get_by_user_and_task(user, task):
            raise EvaluationAlreadyExistsError(user, task)

        return await self.evaluation_repo.create(evaluation, user, task)

    async def get_evaluation_by_id(self, evaluation_id: int) -> Evaluation:
        """
        Get evaluation by id.

        :param evaluation_id: id of an evaluation to get
        :return: Evaluation instance
        :raises EvaluationDoesNotExistError: if the evaluation with the given id does not exist
        """
        evaluation = await self.evaluation_repo.get_by_id(evaluation_id)

        if not evaluation:
            raise EvaluationDoesNotExistError(evaluation_id)

        return evaluation

    async def get_evaluations_of_user_tasks(
        self, user: User, period: EvaluationsPeriod
    ) -> list[Evaluation]:
        """
        Get evaluations of all tasks of the user where they are the assignee.

        :param user: user to get evaluations for
        :param period: period within which to get the evaluations
        :return: list of evaluations
        """
        return await self.evaluation_repo.get_evaluations_of_user_tasks(user, period)

    async def get_avg_evaluation_of_user_tasks(
        self, user: User, period: EvaluationsPeriod
    ) -> float:
        """
        Get average value of evaluations of tasks of the user where they are the assignee.

        :param user: user to get average evaluation for
        :param period: period within which to consider the evaluations
        :return: average evaluation for the given period
        """
        return await self.evaluation_repo.get_avg_evaluation_of_user_tasks(user, period)

    async def update_evaluation(
        self,
        evaluation: Evaluation,
        update_data: EvaluationUpdate,
        task: Task,
    ) -> Evaluation:
        """
        Update an evaluation.

        :param evaluation: evaluation to update
        :param update_data: data to update the evaluation with
        :param task: task to which the evaluation belongs
        :return: updated Evaluation instance
        :raises InvalidTaskStatusError: if the task does not have `TaskStatus.DONE` status
        :raises EvaluationDoesNotBelongToTaskError: if `task.id` and `evaluation.id` are not the same
        """
        if task.id != evaluation.task_id:
            raise EvaluationDoesNotBelongToTaskError(evaluation.id, task.id)

        if task.status != TaskStatus.DONE:
            raise InvalidTaskStatusError(task, TaskStatus.DONE)

        return await self.evaluation_repo.update(evaluation, update_data)

    async def delete_evaluation(self, evaluation: Evaluation, task: Task) -> None:
        """
        Delete an evaluation.

        :param evaluation: evaluation to delete
        :param task: task to which the evaluation belongs
        :return: None
        :raises EvaluationDoesNotBelongToTaskError: if `task.id` and `evaluation.id` are not the same
        """
        if task.id != evaluation.task_id:
            raise EvaluationDoesNotBelongToTaskError(evaluation.id, task.id)

        await self.evaluation_repo.delete(evaluation)
