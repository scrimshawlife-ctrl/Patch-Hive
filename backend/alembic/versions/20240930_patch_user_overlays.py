"""Mutable patch user overlays (notes/favorite/tried) for dual-path patches.

Revision ID: 20240930_patch_user_overlays
Revises: 20240929_visual_inventory_evidence
"""

import sqlalchemy as sa
from alembic import op

revision = "20240930_patch_user_overlays"
down_revision = "20240929_visual_inventory_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patch_user_overlays",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("patch_ref", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tried", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "patch_ref", name="uq_overlay_user_patch_ref"),
    )
    op.create_index("ix_patch_user_overlays_user_id", "patch_user_overlays", ["user_id"])
    op.create_index("ix_patch_user_overlays_patch_ref", "patch_user_overlays", ["patch_ref"])


def downgrade() -> None:
    op.drop_index("ix_patch_user_overlays_patch_ref", table_name="patch_user_overlays")
    op.drop_index("ix_patch_user_overlays_user_id", table_name="patch_user_overlays")
    op.drop_table("patch_user_overlays")
