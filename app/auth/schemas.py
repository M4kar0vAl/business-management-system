from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel

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
                "is_manager",
            },
        )


class UserRead(CustomCreateUpdateDictModel, schemas.BaseUser[UserIdType]):
    is_manager: bool = False


class UserCreate(CustomCreateUpdateDictModel, schemas.BaseUserCreate):
    is_manager: bool | None = False


class UserUpdate(CustomCreateUpdateDictModel, schemas.BaseUserUpdate):
    is_manager: bool | None = None
