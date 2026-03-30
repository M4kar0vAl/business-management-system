from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.auth.schemas import UserRead


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

    user: UserRead
    task_id: Annotated[int, Field(ge=1)]


class CommentUpdate(BaseModel):
    text: str | None = None
