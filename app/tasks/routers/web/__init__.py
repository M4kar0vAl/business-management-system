__all__ = [
    "router",
]

from fastapi import APIRouter

from .comments import router as comments_router
from .evaluations import router as evaluations_router
from .evaluations import user_evaluations_router
from .tasks import router as tasks_router

router = APIRouter(prefix="/tasks")

router.include_router(tasks_router)
router.include_router(comments_router)
router.include_router(evaluations_router)
router.include_router(user_evaluations_router)
