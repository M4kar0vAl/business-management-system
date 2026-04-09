__all__ = [
    "router",
]

from fastapi import APIRouter

from .tasks import router as tasks_router

router = APIRouter(prefix="/tasks")

router.include_router(tasks_router)
