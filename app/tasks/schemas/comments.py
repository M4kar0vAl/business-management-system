from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    created_at: datetime

    user_id: Annotated[int, Field(ge=1)]
    task_id: Annotated[int, Field(ge=1)]


class CommentUpdate(BaseModel):
    text: str | None = None
