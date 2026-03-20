from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel

from app.auth.models import Role
from app.auth.types import UserIdType


class CustomCreateUpdateDictModel(CreateUpdateDictModel):
    def create_update_dict(self):
        return self.model_dump(
            exclude_unset=True,
            exclude={
                # default fields
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
                # custom fields
                "role",
            },
        )


class UserRead(CustomCreateUpdateDictModel, schemas.BaseUser[UserIdType]):
    role: Role = Role.USER


class UserCreate(CustomCreateUpdateDictModel, schemas.BaseUserCreate):
    role: Role | None = Role.USER


class UserUpdate(CustomCreateUpdateDictModel, schemas.BaseUserUpdate):
    role: Role | None = None
