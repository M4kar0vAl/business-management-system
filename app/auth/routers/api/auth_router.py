from fastapi import APIRouter

from app.auth.backend import auth_bearer_db_backend, auth_cookie_db_backend
from app.auth.fastapi_users_instance import fastapi_users_instance
from app.auth.schemas import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(
    fastapi_users_instance.get_auth_router(auth_bearer_db_backend), prefix="/bearer"
)
router.include_router(
    fastapi_users_instance.get_auth_router(auth_cookie_db_backend), prefix="/cookie"
)
router.include_router(fastapi_users_instance.get_register_router(UserRead, UserCreate))
