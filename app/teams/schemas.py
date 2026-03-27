from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.auth.models import Role
from app.auth.schemas import UserRead


class AssignRole(BaseModel):
    role: Role

    @field_validator("role", mode="after")
    @classmethod
    def validate_role(cls, v: Role):
        if v == Role.ADMIN:
            raise ValueError(f"Role {v!r} cannot be assigned")  # noqa: TRY003

        return v


class TeamBase(BaseModel):
    name: Annotated[str, Field(max_length=256)]
    description: Annotated[str, Field(max_length=512)] = ""


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TeamReadFull(TeamRead):
    users: list[UserRead]


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Annotated[str | None, Field(max_length=256)] = None
    description: Annotated[str | None, Field(max_length=512)] = None
