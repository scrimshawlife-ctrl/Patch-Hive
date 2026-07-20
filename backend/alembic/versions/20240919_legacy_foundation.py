"""Create the legacy foundation required by the retained migration history.

Revision ID: 20240919_legacy_foundation
Revises:
Create Date: 2024-09-19 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "20240919_legacy_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create only fields that predate the existing 2024-09-20 revision."""

    # Several retained historical revision identifiers exceed Alembic's
    # default VARCHAR(32), so widen the bookkeeping column before advancing.
    op.alter_column(
        "alembic_version",
        "version_num",
        existing_type=sa.String(length=32),
        type_=sa.String(length=64),
        existing_nullable=False,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("allow_public_avatar", sa.Boolean(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("total_hp", sa.Integer(), nullable=False),
        sa.Column("rows", sa.Integer(), nullable=False),
        sa.Column("hp_per_row", sa.JSON(), nullable=False),
        sa.Column("power_12v_ma", sa.Integer(), nullable=True),
        sa.Column("power_neg12v_ma", sa.Integer(), nullable=True),
        sa.Column("power_5v_ma", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("manufacturer_url", sa.String(length=500), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_reference", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_cases_id", "cases", ["id"])
    op.create_index("ix_cases_brand", "cases", ["brand"])
    op.create_index("ix_cases_name", "cases", ["name"])

    op.create_table(
        "modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("hp", sa.Integer(), nullable=False),
        sa.Column("module_type", sa.String(length=50), nullable=False),
        sa.Column("power_12v_ma", sa.Integer(), nullable=True),
        sa.Column("power_neg12v_ma", sa.Integer(), nullable=True),
        sa.Column("power_5v_ma", sa.Integer(), nullable=True),
        sa.Column("io_ports", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("manufacturer_url", sa.String(length=500), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_reference", sa.String(length=500), nullable=True),
        sa.Column("imported_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_modules_id", "modules", ["id"])
    op.create_index("ix_modules_brand", "modules", ["brand"])
    op.create_index("ix_modules_name", "modules", ["name"])
    op.create_index("ix_modules_module_type", "modules", ["module_type"])

    op.create_table(
        "racks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("generation_seed", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_racks_id", "racks", ["id"])
    op.create_index("ix_racks_user_id", "racks", ["user_id"])
    op.create_index("ix_racks_case_id", "racks", ["case_id"])

    op.create_table(
        "patches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rack_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("connections", sa.JSON(), nullable=False),
        sa.Column("generation_seed", sa.Integer(), nullable=False),
        sa.Column("generation_version", sa.String(length=20), nullable=False),
        sa.Column("engine_config", sa.JSON(), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
        sa.Column("generation_ir", sa.JSON(), nullable=True),
        sa.Column("generation_ir_hash", sa.String(length=32), nullable=True),
        sa.Column("waveform_svg_path", sa.String(length=500), nullable=True),
        sa.Column("waveform_params", sa.JSON(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_patches_id", "patches", ["id"])
    op.create_index("ix_patches_rack_id", "patches", ["rack_id"])
    op.create_index("ix_patches_category", "patches", ["category"])
    op.create_index("ix_patches_generation_ir_hash", "patches", ["generation_ir_hash"])


def downgrade() -> None:
    for table in ("patches", "racks", "modules", "cases", "users"):
        op.drop_table(table)
