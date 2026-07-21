"""Normalized modular synthesizer case catalog.

Revision ID: 20260721_modular_case_catalog
Revises: 20260721_user_style_recipes
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260721_modular_case_catalog"
down_revision = "20260721_user_style_recipes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "case_catalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("manufacturer", sa.String(length=120), nullable=False),
        sa.Column("model", sa.String(length=180), nullable=False),
        sa.Column("format_family", sa.String(length=40), nullable=False),
        sa.Column("production_status", sa.String(length=24), nullable=False, server_default="unknown"),
        sa.Column("powered", sa.Boolean(), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("official_url", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "format_family IN ('eurorack','intellijel_1u','pulplogic_1u','buchla_200','serge_4u','mu_5u','frac','other')",
            name="ck_case_catalog_format_family",
        ),
        sa.UniqueConstraint("slug", name="uq_case_catalog_slug"),
        sa.UniqueConstraint("manufacturer", "model", name="uq_case_catalog_manufacturer_model"),
    )
    op.create_index("ix_case_catalog_slug", "case_catalog", ["slug"], unique=True)
    op.create_index("ix_case_catalog_manufacturer", "case_catalog", ["manufacturer"])
    op.create_index("ix_case_catalog_model", "case_catalog", ["model"])
    op.create_index("ix_case_catalog_format_family", "case_catalog", ["format_family"])
    op.create_index("ix_case_catalog_production_status", "case_catalog", ["production_status"])
    op.create_index("ix_case_catalog_powered", "case_catalog", ["powered"])
    op.create_index("ix_case_catalog_manufacturer_model", "case_catalog", ["manufacturer", "model"])
    op.create_index("ix_case_catalog_format_status", "case_catalog", ["format_family", "production_status"])

    op.create_table(
        "case_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("case_catalog.id", ondelete="CASCADE"), nullable=False),
        sa.Column("revision_key", sa.String(length=80), nullable=False, server_default="default"),
        sa.Column("revision_label", sa.String(length=160), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("capacity_value", sa.Float(), nullable=True),
        sa.Column("capacity_unit", sa.String(length=32), nullable=True),
        sa.Column("usable_capacity_value", sa.Float(), nullable=True),
        sa.Column("depth_min_mm", sa.Float(), nullable=True),
        sa.Column("depth_max_mm", sa.Float(), nullable=True),
        sa.Column("depth_notes", sa.Text(), nullable=True),
        sa.Column("width_mm", sa.Float(), nullable=True),
        sa.Column("height_mm", sa.Float(), nullable=True),
        sa.Column("depth_mm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("materials", sa.Text(), nullable=True),
        sa.Column("mounting_type", sa.String(length=80), nullable=True),
        sa.Column("portable", sa.Boolean(), nullable=True),
        sa.Column("removable_lid", sa.Boolean(), nullable=True),
        sa.Column("close_patched_lid", sa.Boolean(), nullable=True),
        sa.Column("integrated_stand", sa.Boolean(), nullable=True),
        sa.Column("rack_mountable", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "capacity_unit IS NULL OR capacity_unit IN ('hp','mu_space','buchla_panel','serge_panel','frac_width','custom')",
            name="ck_case_revision_capacity_unit",
        ),
        sa.CheckConstraint(
            "confidence IN ('verified','high','medium','low','conflict')",
            name="ck_case_revision_confidence",
        ),
        sa.UniqueConstraint("case_id", "revision_key", name="uq_case_revision_key"),
    )
    op.create_index("ix_case_revision_capacity", "case_revisions", ["capacity_unit", "capacity_value"])
    op.create_index("ix_case_revision_depth", "case_revisions", ["depth_max_mm"])

    op.create_table(
        "case_rows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("revision_id", sa.Integer(), sa.ForeignKey("case_revisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("row_index", sa.Integer(), nullable=False),
        sa.Column("format_family", sa.String(length=40), nullable=False),
        sa.Column("capacity_value", sa.Float(), nullable=True),
        sa.Column("capacity_unit", sa.String(length=32), nullable=True),
        sa.Column("usable_capacity_value", sa.Float(), nullable=True),
        sa.Column("depth_min_mm", sa.Float(), nullable=True),
        sa.Column("depth_max_mm", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("row_index >= 0", name="ck_case_row_nonnegative"),
        sa.UniqueConstraint("revision_id", "row_index", name="uq_case_row_index"),
    )

    op.create_table(
        "case_power_systems",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("revision_id", sa.Integer(), sa.ForeignKey("case_revisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False, server_default="primary"),
        sa.Column("supply_type", sa.String(length=80), nullable=True),
        sa.Column("external_input", sa.String(length=180), nullable=True),
        sa.Column("busboard_type", sa.String(length=120), nullable=True),
        sa.Column("connector_count", sa.Integer(), nullable=True),
        sa.Column("current_pos12_ma", sa.Integer(), nullable=True),
        sa.Column("current_neg12_ma", sa.Integer(), nullable=True),
        sa.Column("current_pos5_ma", sa.Integer(), nullable=True),
        sa.Column("power_watts", sa.Float(), nullable=True),
        sa.Column("zoned_distribution", sa.Boolean(), nullable=True),
        sa.Column("protections", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("connector_count IS NULL OR connector_count >= 0", name="ck_case_power_connectors"),
        sa.CheckConstraint("current_pos12_ma IS NULL OR current_pos12_ma >= 0", name="ck_case_power_pos12"),
        sa.CheckConstraint("current_neg12_ma IS NULL OR current_neg12_ma >= 0", name="ck_case_power_neg12"),
        sa.CheckConstraint("current_pos5_ma IS NULL OR current_pos5_ma >= 0", name="ck_case_power_pos5"),
        sa.UniqueConstraint("revision_id", "name", name="uq_case_power_system_name"),
    )
    op.create_index("ix_case_power_rails", "case_power_systems", ["current_pos12_ma", "current_neg12_ma", "current_pos5_ma"])

    op.create_table(
        "case_features",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("revision_id", sa.Integer(), sa.ForeignKey("case_revisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", sa.String(length=80), nullable=False),
        sa.Column("feature_value", sa.String(length=500), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("revision_id", "feature_key", name="uq_case_feature_key"),
    )
    op.create_index("ix_case_feature_key", "case_features", ["feature_key"])

    op.create_table(
        "case_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("case_catalog.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_name", sa.String(length=160), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("region", sa.String(length=40), nullable=True),
        sa.Column("price_type", sa.String(length=24), nullable=False, server_default="street"),
        sa.Column("in_stock", sa.Boolean(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_case_price_lookup", "case_prices", ["case_id", "currency", "captured_at"])

    op.create_table(
        "case_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("case_catalog.id", ondelete="CASCADE"), nullable=False),
        sa.Column("revision_id", sa.Integer(), sa.ForeignKey("case_revisions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("field_path", sa.String(length=180), nullable=True),
        sa.Column("published_value", sa.Text(), nullable=True),
        sa.Column("normalized_value", sa.Text(), nullable=True),
        sa.Column("discrepancy_note", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "confidence IN ('verified','high','medium','low','conflict')",
            name="ck_case_source_confidence",
        ),
        sa.UniqueConstraint("case_id", "url", "field_path", name="uq_case_source_field"),
    )
    op.create_index("ix_case_source_case_revision", "case_sources", ["case_id", "revision_id"])
    op.create_index("ix_case_source_field", "case_sources", ["field_path"])


def downgrade() -> None:
    op.drop_index("ix_case_source_field", table_name="case_sources")
    op.drop_index("ix_case_source_case_revision", table_name="case_sources")
    op.drop_table("case_sources")
    op.drop_index("ix_case_price_lookup", table_name="case_prices")
    op.drop_table("case_prices")
    op.drop_index("ix_case_feature_key", table_name="case_features")
    op.drop_table("case_features")
    op.drop_index("ix_case_power_rails", table_name="case_power_systems")
    op.drop_table("case_power_systems")
    op.drop_table("case_rows")
    op.drop_index("ix_case_revision_depth", table_name="case_revisions")
    op.drop_index("ix_case_revision_capacity", table_name="case_revisions")
    op.drop_table("case_revisions")
    op.drop_index("ix_case_catalog_format_status", table_name="case_catalog")
    op.drop_index("ix_case_catalog_manufacturer_model", table_name="case_catalog")
    op.drop_index("ix_case_catalog_powered", table_name="case_catalog")
    op.drop_index("ix_case_catalog_production_status", table_name="case_catalog")
    op.drop_index("ix_case_catalog_format_family", table_name="case_catalog")
    op.drop_index("ix_case_catalog_model", table_name="case_catalog")
    op.drop_index("ix_case_catalog_manufacturer", table_name="case_catalog")
    op.drop_index("ix_case_catalog_slug", table_name="case_catalog")
    op.drop_table("case_catalog")
