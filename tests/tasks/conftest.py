import pytest

from app.auth.models import User
from app.tasks.models import Comment, Task
from app.tasks.repositories import CommentRepository, TaskRepository
from app.tasks.schemas import CommentCreate, TaskCreate
from app.tasks.services import CommentService, TaskService


@pytest.fixture
async def task_repository(session):
    return TaskRepository(session)


@pytest.fixture
async def comment_repository(session):
    return CommentRepository(session)


@pytest.fixture
async def task_service(uow, user_manager):
    return TaskService(uow, user_manager)


@pytest.fixture
async def comment_service(uow):
    return CommentService(uow)


@pytest.fixture
async def create_task(task_service):

    async def _create_task(
        task: TaskCreate, author: User, assignee: User | None = None
    ) -> Task:
        created_task = await task_service.create_task(task, author)

        if assignee:
            created_task.assignee_id = assignee.id

        await task_service.uow.flush()
        return created_task

    return _create_task


@pytest.fixture
async def create_comment(comment_service):

    async def _create_comment(
        comment: CommentCreate, task_id: int, author: User
    ) -> Comment:
        created_comment = await comment_service.create_comment(comment, author, task_id)
        await comment_service.uow.flush()
        return created_comment

    return _create_comment
