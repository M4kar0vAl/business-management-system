__all__ = [
    "router",
]

from fastapi import APIRouter, Depends

from app import responses
from app.auth.fastapi_users_instance import current_active_user

from .comments import router as comments_router
from .evaluations import router as evaluations_router
from .evaluations import user_evaluations_router
from .tasks import router as tasks_router

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(current_active_user)],
    responses={**responses.UNAUTHORIZED_RESPONSE},
)

router.include_router(tasks_router)
router.include_router(comments_router)
router.include_router(evaluations_router)
router.include_router(user_evaluations_router)
