"""alter Task and Comment: datetime fields timezone aware

Revision ID: c12aec13c853
Revises: ae95cce840b3
Create Date: 2026-03-28 15:37:35.900765

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c12aec13c853"
down_revision: str | Sequence[str] | None = "ae95cce840b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "comments",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "tasks",
        "deadline",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "tasks",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "tasks",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "tasks",
        "deadline",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "comments",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )
