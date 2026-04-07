from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.mixins import IdIntPkMixin
from app.models import Base

if TYPE_CHECKING:
    from app.auth.models import User


meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column(
        "meeting_id", ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Meeting(IdIntPkMixin, Base):
    __tablename__ = "meetings"

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    created_by: Mapped[User] = relationship(
        back_populates="created_meetings", foreign_keys=created_by_id
    )
    participants: Mapped[list[User]] = relationship(
        back_populates="meetings", secondary=meeting_participants, passive_deletes=True
    )

    __table_args__ = (
        CheckConstraint("end_time > start_time", name="check_end_after_start"),
    )

    def __str__(self):
        return f"Meeting [{self.start_time} - {self.end_time}]"
