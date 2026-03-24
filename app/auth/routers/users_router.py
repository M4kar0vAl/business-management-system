from fastapi import APIRouter

from app.auth.fastapi_users_instance import fastapi_users_instance
from app.auth.schemas import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(fastapi_users_instance.get_users_router(UserRead, UserUpdate))
