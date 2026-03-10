from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr

from app.auth.types import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    is_manager: bool = False


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str


class UserUpdate(CreateUpdateDictModel):
    email: EmailStr | None = None
    password: str | None = None
