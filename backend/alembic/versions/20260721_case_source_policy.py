"""Case source provenance and licensing packets.

Revision ID: 20260721_case_source_policy
Revises: 20260721_modular_case_catalog
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260721_case_source_policy"
down_revision = "20260721_modular_case_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_source_policy_packets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("case_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_record_id", sa.String(length=240), nullable=True),
        sa.Column("access_basis", sa.String(length=40), nullable=False, server_default="unknown"),
        sa.Column("license_status", sa.String(length=40), nullable=False, server_default="unknown"),
        sa.Column("evidence_status", sa.String(length=40), nullable=False, server_default="UNKNOWN"),
        sa.Column("review_state", sa.String(length=32), nullable=False, server_default="unreviewed"),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("normalizer_version", sa.String(length=64), nullable=True),
        sa.Column("reviewed_by", sa.String(length=160), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "access_basis IN ('official_publication','authorized_feed','licensed_dataset','user_authorized_export','manual_research','user_upload','provider_inference','unknown')",
            name="ck_case_source_policy_access_basis",
        ),
        sa.CheckConstraint(
            "evidence_status IN ('MANUFACTURER_CONFIRMED','MANUAL_CONFIRMED','REGISTRY_CONFIRMED','USER_CONFIRMED','RETAILER_OBSERVED','CATALOG_OBSERVED','INFERRED','CONFLICTED','REJECTED','UNKNOWN','NOT_COMPUTABLE')",
            name="ck_case_source_policy_evidence_status",
        ),
        sa.CheckConstraint(
            "review_state IN ('unreviewed','pending','accepted','rejected','blocked','conflicted','needs_review')",
            name="ck_case_source_policy_review_state",
        ),
        sa.UniqueConstraint("source_id", name="uq_case_source_policy_source"),
    )
    op.create_index("ix_case_source_policy_evidence", "case_source_policy_packets", ["evidence_status", "review_state"])
    op.create_index("ix_case_source_policy_access", "case_source_policy_packets", ["access_basis", "license_status"])
    op.create_index("ix_case_source_policy_hash", "case_source_policy_packets", ["content_hash"])


def downgrade() -> None:
    op.drop_index("ix_case_source_policy_hash", table_name="case_source_policy_packets")
    op.drop_index("ix_case_source_policy_access", table_name="case_source_policy_packets")
    op.drop_index("ix_case_source_policy_evidence", table_name="case_source_policy_packets")
    op.drop_table("case_source_policy_packets")
