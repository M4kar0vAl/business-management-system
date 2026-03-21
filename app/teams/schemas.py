from typing import Annotated

from pydantic import BaseModel, Field

from app.auth.schemas import UserRead


class TeamBase(BaseModel):
    name: Annotated[str, Field(max_length=256)]
    description: Annotated[str, Field(max_length=512)] = ""


class TeamRead(TeamBase):
    id: int


class TeamReadFull(TeamRead):
    users: list[UserRead]


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Annotated[str | None, Field(max_length=256)] = None
    description: Annotated[str | None, Field(max_length=512)] = None
