from fastapi_users import schemas

from app.auth.types import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    is_manager: bool = False


class UserCreate(schemas.BaseUserCreate):
    is_manager: bool | None = False


class UserUpdate(schemas.BaseUserUpdate):
    is_manager: bool | None = None
