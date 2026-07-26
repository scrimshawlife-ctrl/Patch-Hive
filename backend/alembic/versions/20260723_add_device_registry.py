"""Add Device Registry tables (Manufacturer, Family, Model, Revision, Port, Control, Capability).

Revision ID: 20260723_add_device_registry
Revises: 20260722_module_catalog_source
Create Date: 2026-07-23

This adds the canonical Device Registry hierarchy for the public Product Database (PDB).
See backend/registry/models.py and docs/DEVICE_REGISTRY.md.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260723_add_device_registry"
down_revision = "20260722_module_catalog_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Manufacturers
    op.create_table(
        "manufacturers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canonical_name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_manufacturers_id", "manufacturers", ["id"])
    op.create_index("ix_manufacturers_canonical_name", "manufacturers", ["canonical_name"])
    op.create_index("ix_manufacturers_slug", "manufacturers", ["slug"])

    # Device Families
    op.create_table(
        "device_families",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("manufacturer_id", sa.Integer(), sa.ForeignKey("manufacturers.id"), nullable=False),
        sa.Column("canonical_name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
    )
    op.create_index("ix_device_families_id", "device_families", ["id"])
    op.create_index("ix_device_families_manufacturer_id", "device_families", ["manufacturer_id"])

    # Device Models
    op.create_table(
        "device_models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("manufacturer_id", sa.Integer(), sa.ForeignKey("manufacturers.id"), nullable=False),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("device_families.id"), nullable=True),
        sa.Column("canonical_name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("device_type", sa.String(length=50), nullable=True),
        sa.Column("format", sa.String(length=30), nullable=True),
        sa.Column("hp", sa.Integer(), nullable=True),
        sa.Column("depth_mm", sa.Float(), nullable=True),
        sa.Column("release_state", sa.String(length=20), nullable=True),
        sa.Column("official_sources", sa.JSON(), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_device_models_id", "device_models", ["id"])
    op.create_index("ix_device_models_manufacturer_id", "device_models", ["manufacturer_id"])
    op.create_index("ix_device_models_slug", "device_models", ["slug"])

    # Device Revisions
    op.create_table(
        "device_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_model_id", sa.Integer(), sa.ForeignKey("device_models.id"), nullable=False),
        sa.Column("revision_label", sa.String(length=50), nullable=False),
        sa.Column("panel_variant", sa.String(length=50), nullable=True),
        sa.Column("firmware_constraints", sa.JSON(), nullable=True),
        sa.Column("physical_changes", sa.JSON(), nullable=True),
        sa.Column("functional_changes", sa.JSON(), nullable=True),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
    )
    op.create_index("ix_device_revisions_id", "device_revisions", ["id"])
    op.create_index("ix_device_revisions_device_model_id", "device_revisions", ["device_model_id"])

    # Ports
    op.create_table(
        "ports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("revision_id", sa.Integer(), sa.ForeignKey("device_revisions.id"), nullable=False),
        sa.Column("canonical_label", sa.String(length=100), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=True),
        sa.Column("signal_class", sa.String(length=30), nullable=True),
        sa.Column("connector_type", sa.String(length=30), nullable=True),
        sa.Column("channel_count", sa.Integer(), nullable=True),
        sa.Column("voltage_or_level_domain", sa.String(length=50), nullable=True),
        sa.Column("evidence_status", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_ports_id", "ports", ["id"])
    op.create_index("ix_ports_revision_id", "ports", ["revision_id"])

    # Controls
    op.create_table(
        "controls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("revision_id", sa.Integer(), sa.ForeignKey("device_revisions.id"), nullable=False),
        sa.Column("canonical_label", sa.String(length=100), nullable=False),
        sa.Column("control_type", sa.String(length=30), nullable=True),
        sa.Column("range", sa.JSON(), nullable=True),
        sa.Column("units", sa.String(length=20), nullable=True),
        sa.Column("discrete_values", sa.JSON(), nullable=True),
        sa.Column("default_or_neutral_position", sa.String(length=50), nullable=True),
        sa.Column("evidence_status", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_controls_id", "controls", ["id"])
    op.create_index("ix_controls_revision_id", "controls", ["revision_id"])

    # Capabilities
    op.create_table(
        "capabilities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canonical_type", sa.String(length=50), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("constraints", sa.JSON(), nullable=True),
        sa.Column("required_ports", sa.JSON(), nullable=True),
        sa.Column("required_controls", sa.JSON(), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
    )
    op.create_index("ix_capabilities_id", "capabilities", ["id"])
    op.create_index("ix_capabilities_canonical_type", "capabilities", ["canonical_type"])


def downgrade() -> None:
    op.drop_index("ix_capabilities_canonical_type", table_name="capabilities")
    op.drop_index("ix_capabilities_id", table_name="capabilities")
    op.drop_table("capabilities")

    op.drop_index("ix_controls_revision_id", table_name="controls")
    op.drop_index("ix_controls_id", table_name="controls")
    op.drop_table("controls")

    op.drop_index("ix_ports_revision_id", table_name="ports")
    op.drop_index("ix_ports_id", table_name="ports")
    op.drop_table("ports")

    op.drop_index("ix_device_revisions_device_model_id", table_name="device_revisions")
    op.drop_index("ix_device_revisions_id", table_name="device_revisions")
    op.drop_table("device_revisions")

    op.drop_index("ix_device_models_slug", table_name="device_models")
    op.drop_index("ix_device_models_manufacturer_id", table_name="device_models")
    op.drop_index("ix_device_models_id", table_name="device_models")
    op.drop_table("device_models")

    op.drop_index("ix_device_families_manufacturer_id", table_name="device_families")
    op.drop_index("ix_device_families_id", table_name="device_families")
    op.drop_table("device_families")

    op.drop_index("ix_manufacturers_slug", table_name="manufacturers")
    op.drop_index("ix_manufacturers_canonical_name", table_name="manufacturers")
    op.drop_index("ix_manufacturers_id", table_name="manufacturers")
    op.drop_table("manufacturers")
