from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.mixins import IdIntPkMixin
from app.models import Base

if TYPE_CHECKING:
    from app.auth.models import User


class Team(IdIntPkMixin, Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(256), unique=True)
    description: Mapped[str] = mapped_column(String(512), default="", server_default="")

    users: Mapped[list[User]] = relationship(back_populates="team")
