"""add team_id to user model

Revision ID: d8c655a0339e
Revises: f7b71f64ab3a
Create Date: 2026-03-20 20:34:48.373307

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8c655a0339e"
down_revision: str | Sequence[str] | None = "f7b71f64ab3a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("teams_name_key"), "teams", type_="unique")
    op.create_unique_constraint(op.f("uq_teams_name"), "teams", ["name"])
    op.add_column("users", sa.Column("team_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_users_team_id_teams"),
        "users",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="set null",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("fk_users_team_id_teams"), "users", type_="foreignkey")
    op.drop_column("users", "team_id")
    op.drop_constraint(op.f("uq_teams_name"), "teams", type_="unique")
    op.create_unique_constraint(
        op.f("teams_name_key"), "teams", ["name"], postgresql_nulls_not_distinct=False
    )
