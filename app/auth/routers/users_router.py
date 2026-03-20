from fastapi import APIRouter

from app.auth.fastapi_users import fastapi_users
from app.auth.schemas import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
