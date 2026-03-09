"""delete users role; add users is_manager

Revision ID: 8af7839a6f46
Revises: 2dfb8b49631c
Create Date: 2026-03-09 18:48:25.117954

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8af7839a6f46"
down_revision: str | Sequence[str] | None = "2dfb8b49631c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "is_manager", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.drop_column("users", "role")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "role",
            postgresql.ENUM("USER", "MANAGER", "ADMIN", name="role"),
            server_default="USER",
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("users", "is_manager")
