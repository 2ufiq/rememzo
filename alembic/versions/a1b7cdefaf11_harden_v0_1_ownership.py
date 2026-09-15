"""Harden v0.1 ownership constraints.

Revision ID: a1b7cdefaf11
Revises: 0326e31bf894
Create Date: 2026-09-15 19:39:10.591203+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b7cdefaf11"
down_revision: str | Sequence[str] | None = "0326e31bf894"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NAMING_CONVENTION = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def set_sqlite_foreign_keys(enabled: bool) -> None:
    if op.get_bind().dialect.name != "sqlite":
        return
    value = "ON" if enabled else "OFF"
    with op.get_context().autocommit_block():
        op.get_bind().exec_driver_sql(f"PRAGMA foreign_keys={value}")


def upgrade() -> None:
    """Remove slugs and enforce project ownership relationships."""
    set_sqlite_foreign_keys(False)

    with op.batch_alter_table(
        "memberships", recreate="always", naming_convention=NAMING_CONVENTION
    ) as batch_op:
        batch_op.drop_constraint("fk_memberships_project_id_projects", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_memberships_project_id_projects",
            "projects",
            ["project_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table(
        "memories", recreate="always", naming_convention=NAMING_CONVENTION
    ) as batch_op:
        batch_op.drop_constraint("fk_memories_project_id_projects", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_memories_project_id_projects",
            "projects",
            ["project_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.create_check_constraint(
            "ck_memories_scope_project",
            "(scope = 'user' AND project_id IS NULL) OR "
            "(scope = 'project' AND project_id IS NOT NULL)",
        )

    with op.batch_alter_table("projects", recreate="always") as batch_op:
        batch_op.drop_column("slug")

    set_sqlite_foreign_keys(True)


def downgrade() -> None:
    """Restore the original project slug and foreign keys."""
    set_sqlite_foreign_keys(False)

    with op.batch_alter_table("projects", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(), nullable=True))

    op.execute("UPDATE projects SET slug = CAST(id AS VARCHAR) WHERE slug IS NULL")

    with op.batch_alter_table("projects", recreate="always") as batch_op:
        batch_op.alter_column("slug", existing_type=sa.String(), nullable=False)
        batch_op.create_unique_constraint("uq_projects_slug", ["slug"])

    with op.batch_alter_table(
        "memories", recreate="always", naming_convention=NAMING_CONVENTION
    ) as batch_op:
        batch_op.drop_constraint("ck_memories_scope_project", type_="check")
        batch_op.drop_constraint("fk_memories_project_id_projects", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_memories_project_id_projects", "projects", ["project_id"], ["id"]
        )

    with op.batch_alter_table(
        "memberships", recreate="always", naming_convention=NAMING_CONVENTION
    ) as batch_op:
        batch_op.drop_constraint("fk_memberships_project_id_projects", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_memberships_project_id_projects", "projects", ["project_id"], ["id"]
        )

    set_sqlite_foreign_keys(True)
