"""Add provenance source column on module_catalog.

Revision ID: 20260722_module_catalog_source
Revises: 20260721_module_depth_mm
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260722_module_catalog_source"
down_revision = "20260721_module_depth_mm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "module_catalog",
        sa.Column("source", sa.String(length=50), nullable=True),
    )
    op.create_index("ix_module_catalog_source", "module_catalog", ["source"])
    # Existing rows admitted via Synth Catalog Research seed (phase2/phase3).
    op.execute(
        "UPDATE module_catalog SET source = 'SynthCatalogResearch' "
        "WHERE source IS NULL"
    )


def downgrade() -> None:
    op.drop_index("ix_module_catalog_source", table_name="module_catalog")
    op.drop_column("module_catalog", "source")
