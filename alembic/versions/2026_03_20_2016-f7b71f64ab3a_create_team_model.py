"""create team model

Revision ID: f7b71f64ab3a
Revises: 2dfb8b49631c
Create Date: 2026-03-20 20:16:57.309010

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f7b71f64ab3a"
down_revision: str | Sequence[str] | None = "2dfb8b49631c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column(
            "description", sa.String(length=512), server_default="", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("teams")
