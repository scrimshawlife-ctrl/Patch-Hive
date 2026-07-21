"""Add Design Engine columns to canonical_exports.

Revision ID: 20260721_design_engine
Revises: 20240930_patch_user_overlays
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260721_design_engine"
down_revision = "20240930_patch_user_overlays"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("canonical_exports", sa.Column("style_recipe_hash", sa.String(64), nullable=True))
    op.add_column("canonical_exports", sa.Column("request_style_recipe_json", sa.JSON(), nullable=True))
    op.add_column(
        "canonical_exports", sa.Column("resolved_style_recipe_json", sa.JSON(), nullable=True)
    )
    op.add_column("canonical_exports", sa.Column("resolved_tier", sa.String(20), nullable=True))
    op.add_column(
        "canonical_exports", sa.Column("design_engine_version", sa.String(64), nullable=True)
    )
    op.add_column("canonical_exports", sa.Column("book_profile", sa.String(40), nullable=True))
    op.add_column(
        "canonical_exports", sa.Column("library_content_hash", sa.String(64), nullable=True)
    )
    op.add_column("canonical_exports", sa.Column("composition_hash", sa.String(64), nullable=True))
    op.add_column(
        "canonical_exports", sa.Column("pack_manifest_hash", sa.String(64), nullable=True)
    )
    op.add_column("canonical_exports", sa.Column("artifact_uri", sa.String(512), nullable=True))
    op.add_column(
        "canonical_exports",
        sa.Column("fulfill_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "canonical_exports", sa.Column("running_started_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("canonical_exports", sa.Column("error_code", sa.String(100), nullable=True))


def downgrade() -> None:
    for col in (
        "error_code",
        "running_started_at",
        "fulfill_attempts",
        "artifact_uri",
        "pack_manifest_hash",
        "composition_hash",
        "library_content_hash",
        "book_profile",
        "design_engine_version",
        "resolved_tier",
        "resolved_style_recipe_json",
        "request_style_recipe_json",
        "style_recipe_hash",
    ):
        op.drop_column("canonical_exports", col)
