from typing import Annotated

from fastapi import Depends

from app.auth.dependencies import get_user_manager
from app.auth.user_manager import UserManager
from app.dependencies import UOWDep
from app.tasks.services import CommentService, TaskService


async def get_task_service(
    uow: UOWDep, user_manager: Annotated[UserManager, Depends(get_user_manager)]
):
    yield TaskService(uow, user_manager)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


async def get_comments_service(uow: UOWDep):
    yield CommentService(uow)


CommentServiceDep = Annotated[CommentService, Depends(get_comments_service)]
