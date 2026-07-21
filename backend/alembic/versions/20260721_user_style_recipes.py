"""User style recipe library + export.style_recipe_id.

Revision ID: 20260721_user_style_recipes
Revises: 20260721_design_engine
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260721_user_style_recipes"
down_revision = "20260721_design_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_style_recipes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recipe_json", sa.JSON(), nullable=False),
        sa.Column("recipe_hash", sa.String(length=64), nullable=False),
        sa.Column("is_shared", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "name", name="uq_user_style_recipes_name"),
    )
    op.create_index("ix_user_style_recipes_user_id", "user_style_recipes", ["user_id"])
    op.create_index("ix_user_style_recipes_recipe_hash", "user_style_recipes", ["recipe_hash"])
    op.add_column(
        "canonical_exports",
        sa.Column(
            "style_recipe_id",
            sa.String(length=64),
            sa.ForeignKey("user_style_recipes.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_canonical_exports_style_recipe_id", "canonical_exports", ["style_recipe_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_canonical_exports_style_recipe_id", table_name="canonical_exports")
    op.drop_column("canonical_exports", "style_recipe_id")
    op.drop_index("ix_user_style_recipes_recipe_hash", table_name="user_style_recipes")
    op.drop_index("ix_user_style_recipes_user_id", table_name="user_style_recipes")
    op.drop_table("user_style_recipes")
