from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.mixins import IdIntPkMixin
from app.models import Base


class Team(IdIntPkMixin, Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(256), unique=True)
    description: Mapped[str] = mapped_column(String(512), default="", server_default="")
