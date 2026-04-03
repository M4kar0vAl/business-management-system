import pytest

from app.auth.models import User
from app.tasks.models import Comment, Evaluation, Task
from app.tasks.repositories import CommentRepository, EvaluationRepository
from app.tasks.schemas import CommentCreate, EvaluationCreate
from app.tasks.services import CommentService, EvaluationService


@pytest.fixture
async def comment_repository(session):
    return CommentRepository(session)


@pytest.fixture
async def comment_service(uow):
    return CommentService(uow)


@pytest.fixture
async def create_comment(comment_service):

    async def _create_comment(
        comment: CommentCreate, task: Task, author: User
    ) -> Comment:
        created_comment = await comment_service.create_comment(comment, author, task)
        await comment_service.uow.flush()
        return created_comment

    return _create_comment


@pytest.fixture
async def evaluations_repository(session):
    return EvaluationRepository(session)


@pytest.fixture
async def evaluations_service(uow):
    return EvaluationService(uow)


@pytest.fixture
async def create_evaluation(evaluations_service):

    async def _create_evaluation(
        evaluation: EvaluationCreate, task: Task, author: User
    ) -> Evaluation:
        created_evaluation = await evaluations_service.create_evaluation(
            evaluation, author, task
        )
        await evaluations_service.uow.flush()
        return created_evaluation

    return _create_evaluation
