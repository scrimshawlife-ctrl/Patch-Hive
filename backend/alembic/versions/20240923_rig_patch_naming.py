"""Add rig/patch naming provenance and run linkage.

Revision ID: 20240923_rig_patch_naming
Revises: 20240922_admin_console
Create Date: 2024-09-23 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "20240923_rig_patch_naming"
down_revision = "20240922_admin_console"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("racks", sa.Column("name_suggested", sa.String(length=200), nullable=True))
    op.execute("UPDATE racks SET name_suggested = name WHERE name_suggested IS NULL")

    op.add_column("patches", sa.Column("suggested_name", sa.String(length=200), nullable=True))
    op.add_column("patches", sa.Column("name_override", sa.String(length=200), nullable=True))
    op.add_column("patches", sa.Column("run_id", sa.Integer(), nullable=True))
    op.create_index("ix_patches_run_id", "patches", ["run_id"], unique=False)
    op.create_foreign_key(
        "fk_patches_run_id",
        "patches",
        "runs",
        ["run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute("UPDATE patches SET suggested_name = name WHERE suggested_name IS NULL")


def downgrade() -> None:
    op.drop_constraint("fk_patches_run_id", "patches", type_="foreignkey")
    op.drop_index("ix_patches_run_id", table_name="patches")
    op.drop_column("patches", "run_id")
    op.drop_column("patches", "name_override")
    op.drop_column("patches", "suggested_name")

    op.drop_column("racks", "name_suggested")
