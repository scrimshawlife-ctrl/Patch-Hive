"""Persist visual inventory revisions and image evidence assets.

Revision ID: 20240929_visual_inventory_evidence
Revises: 20240928_fix_schema_gaps
"""

import sqlalchemy as sa
from alembic import op

revision = "20240929_visual_inventory_evidence"
down_revision = "20240928_fix_schema_gaps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_inventory_revisions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("system_id", sa.String(length=128), nullable=False),
        sa.Column("rack_id", sa.Integer(), nullable=True),
        sa.Column("previous_revision_id", sa.String(length=64), nullable=True),
        sa.Column("schema_version", sa.String(length=64), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("unresolved_candidate_ids", sa.JSON(), nullable=False),
        sa.Column("canonical_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["previous_revision_id"],
            ["system_inventory_revisions.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("canonical_hash"),
    )
    op.create_index(
        "ix_system_inventory_revisions_system_id",
        "system_inventory_revisions",
        ["system_id"],
    )
    op.create_index(
        "ix_system_inventory_revisions_rack_id",
        "system_inventory_revisions",
        ["rack_id"],
    )
    op.create_index(
        "ix_system_inventory_revisions_canonical_hash",
        "system_inventory_revisions",
        ["canonical_hash"],
    )

    op.create_table(
        "image_assets",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("rack_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("media_type", sa.String(length=64), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("byte_length", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("retention_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consent_provider_processing", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_image_assets_rack_id", "image_assets", ["rack_id"])
    op.create_index("ix_image_assets_user_id", "image_assets", ["user_id"])
    op.create_index("ix_image_assets_content_sha256", "image_assets", ["content_sha256"])

    op.create_table(
        "classification_evidence_records",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("image_asset_id", sa.String(length=64), nullable=False),
        sa.Column("inventory_revision_id", sa.String(length=64), nullable=True),
        sa.Column("evidence_packet", sa.JSON(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("pipeline_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["image_asset_id"], ["image_assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["inventory_revision_id"],
            ["system_inventory_revisions.id"],
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_classification_evidence_records_image_asset_id",
        "classification_evidence_records",
        ["image_asset_id"],
    )
    op.create_index(
        "ix_classification_evidence_records_inventory_revision_id",
        "classification_evidence_records",
        ["inventory_revision_id"],
    )


def downgrade() -> None:
    op.drop_table("classification_evidence_records")
    op.drop_table("image_assets")
    op.drop_table("system_inventory_revisions")
