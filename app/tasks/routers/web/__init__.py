__all__ = [
    "router",
]

from fastapi import APIRouter

from .comments import router as comments_router
from .tasks import router as tasks_router

router = APIRouter(prefix="/tasks")

router.include_router(tasks_router)
router.include_router(comments_router)
