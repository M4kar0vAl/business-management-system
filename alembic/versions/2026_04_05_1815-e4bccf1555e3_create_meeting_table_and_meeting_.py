"""create Meeting table and meeting_participants association table

Revision ID: e4bccf1555e3
Revises: e979b2ca64ec
Create Date: 2026-04-05 18:15:21.919551

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e4bccf1555e3"
down_revision: str | Sequence[str] | None = "e979b2ca64ec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_meetings")),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
            name=op.f("fk_meetings_created_by_id_users"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "end_time > start_time", name=op.f("ck_meetings_check_end_after_start")
        ),
    )
    op.create_table(
        "meeting_participants",
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint(
            "meeting_id", "user_id", name=op.f("pk_meeting_participants")
        ),
        sa.ForeignKeyConstraint(
            ["meeting_id"],
            ["meetings.id"],
            name=op.f("fk_meeting_participants_meeting_id_meetings"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_meeting_participants_user_id_users"),
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("meeting_participants")
    op.drop_table("meetings")
