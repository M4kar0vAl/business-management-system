from fastapi import APIRouter

from app.auth.backend import authentication_backend
from app.auth.fastapi_users_instance import fastapi_users_instance
from app.auth.schemas import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(fastapi_users_instance.get_auth_router(authentication_backend))
router.include_router(fastapi_users_instance.get_register_router(UserRead, UserCreate))
