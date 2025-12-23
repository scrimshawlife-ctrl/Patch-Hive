"""Acceptance test scaffolding additions.

Revision ID: 20240926_acceptance_features
Revises: 20240922_admin_console
Create Date: 2024-09-26
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240926_acceptance_features"
down_revision = "20240922_admin_console"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patches", sa.Column("run_id", sa.Integer(), nullable=True))
    op.add_column("patches", sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
    op.create_index("ix_patches_run_id", "patches", ["run_id"], unique=False)
    op.create_foreign_key("fk_patches_run_id", "patches", "runs", ["run_id"], ["id"], ondelete="SET NULL")

    op.add_column("exports", sa.Column("run_id", sa.Integer(), nullable=True))
    op.create_index("ix_exports_run_id", "exports", ["run_id"], unique=False)
    op.create_foreign_key("fk_exports_run_id", "exports", "runs", ["run_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "pending_functions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("function_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("canonical_function", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_pending_functions_module_id", "pending_functions", ["module_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_pending_functions_module_id", table_name="pending_functions")
    op.drop_table("pending_functions")

    op.drop_constraint("fk_exports_run_id", "exports", type_="foreignkey")
    op.drop_index("ix_exports_run_id", table_name="exports")
    op.drop_column("exports", "run_id")

    op.drop_constraint("fk_patches_run_id", "patches", type_="foreignkey")
    op.drop_index("ix_patches_run_id", table_name="patches")
    op.drop_column("patches", "tags")
    op.drop_column("patches", "run_id")
