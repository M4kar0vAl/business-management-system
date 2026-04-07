from fastapi import APIRouter

from app.auth.routers import auth_router, users_router
from app.meetings.routers import router as meetings_router
from app.tasks.routers import router as tasks_router
from app.teams.routers import router as teams_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(meetings_router)
router.include_router(tasks_router)
router.include_router(teams_router)
