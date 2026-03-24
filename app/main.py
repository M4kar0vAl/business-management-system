import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin import register_admin_views
from app.auth.actions import create_user
from app.auth.routers import auth_router, users_router
from app.config import settings
from app.exception_handlers import register_exception_handlers
from app.teams.routers import router as teams_router

log = logging.getLogger(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    try:
        await create_user(
            settings.USER.ADMIN_EMAIL,
            settings.USER.ADMIN_PASSWORD.get_secret_value(),
            True,
        )
    except Exception as e:
        log.warning("Could not create superuser: %r", e)

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(teams_router)

register_admin_views(app)

register_exception_handlers(app)
