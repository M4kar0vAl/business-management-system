import pytest

from app.auth.models import User
from app.tasks.models import Comment, Task
from app.tasks.repositories import CommentRepository
from app.tasks.schemas import CommentCreate
from app.tasks.services import CommentService


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
