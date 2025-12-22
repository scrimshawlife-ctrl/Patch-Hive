"""Add admin console models and user/module fields.

Revision ID: 20240922_admin_console
Revises: 20240921_make_referrals_append_only
Create Date: 2024-09-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "20240922_admin_console"
down_revision = "20240921_make_referrals_append_only"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True))
    op.execute("UPDATE users SET role = 'User' WHERE role IS NULL")
    op.alter_column("users", "role", nullable=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.add_column("modules", sa.Column("status", sa.String(length=20), nullable=True))
    op.add_column("modules", sa.Column("replacement_module_id", sa.Integer(), nullable=True))
    op.add_column("modules", sa.Column("deprecated_at", sa.DateTime(), nullable=True))
    op.add_column("modules", sa.Column("tombstoned_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE modules SET status = 'active' WHERE status IS NULL")
    op.alter_column("modules", "status", nullable=False)
    op.create_index("ix_modules_status", "modules", ["status"], unique=False)
    op.create_foreign_key(
        "fk_modules_replacement",
        "modules",
        "modules",
        ["replacement_module_id"],
        ["id"],
    )

    op.create_table(
        "admin_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("actor_role", sa.String(length=20), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=50), nullable=True),
        sa.Column("delta_json", sa.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_admin_audit_log_actor_user_id", "admin_audit_log", ["actor_user_id"], unique=False)

    op.create_table(
        "gallery_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_key", sa.String(length=200), nullable=False),
        sa.Column("revision_id", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_gallery_revisions_module_key", "gallery_revisions", ["module_key"], unique=False)
    op.create_index("ix_gallery_revisions_revision_id", "gallery_revisions", ["revision_id"], unique=False)

    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rack_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_runs_rack_id", "runs", ["rack_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_runs_rack_id", table_name="runs")
    op.drop_table("runs")

    op.drop_index("ix_gallery_revisions_revision_id", table_name="gallery_revisions")
    op.drop_index("ix_gallery_revisions_module_key", table_name="gallery_revisions")
    op.drop_table("gallery_revisions")

    op.drop_index("ix_admin_audit_log_actor_user_id", table_name="admin_audit_log")
    op.drop_table("admin_audit_log")

    op.drop_constraint("fk_modules_replacement", "modules", type_="foreignkey")
    op.drop_index("ix_modules_status", table_name="modules")
    op.drop_column("modules", "tombstoned_at")
    op.drop_column("modules", "deprecated_at")
    op.drop_column("modules", "replacement_module_id")
    op.drop_column("modules", "status")

    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
    op.drop_column("users", "display_name")
