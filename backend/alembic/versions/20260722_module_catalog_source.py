"""Ensure module_catalog exists and add provenance source column.

Revision ID: 20260722_module_catalog_source
Revises: 20260721_module_depth_mm
Create Date: 2026-07-22

``module_catalog`` was historically created via SQLAlchemy ``create_all``
(not the Alembic foundation chain). Fresh CI DBs that only run ``alembic
upgrade head`` therefore lack the table. This revision:

1. Creates ``module_catalog`` (with ``source``) when missing
2. Adds ``source`` + index when the table already exists without it
3. Backfills null sources to SynthCatalogResearch
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260722_module_catalog_source"
down_revision = "20260721_module_depth_mm"
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    bind = op.get_bind()
    return set(inspect(bind).get_table_names())


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    return {c["name"] for c in inspect(bind).get_columns(table)}


def upgrade() -> None:
    tables = _table_names()

    if "module_catalog" not in tables:
        # Full lightweight catalog schema (matches modules.catalog.ModuleCatalog).
        op.create_table(
            "module_catalog",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("modulargrid_id", sa.Integer(), nullable=True),
            sa.Column("slug", sa.String(length=200), nullable=False),
            sa.Column("brand", sa.String(length=100), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("hp", sa.Integer(), nullable=True),
            sa.Column("category", sa.String(length=50), nullable=True),
            sa.Column("image_url", sa.String(length=500), nullable=True),
            sa.Column("modulargrid_url", sa.String(length=500), nullable=True),
            sa.Column("manufacturer_url", sa.String(length=500), nullable=True),
            sa.Column("is_available", sa.String(length=20), nullable=True),
            sa.Column("source", sa.String(length=50), nullable=True),
            sa.Column("created_at", sa.String(length=50), nullable=True),
            sa.Column("updated_at", sa.String(length=50), nullable=True),
        )
        op.create_index("ix_module_catalog_id", "module_catalog", ["id"])
        op.create_index(
            "ix_module_catalog_modulargrid_id",
            "module_catalog",
            ["modulargrid_id"],
            unique=True,
        )
        op.create_index("ix_module_catalog_slug", "module_catalog", ["slug"], unique=True)
        op.create_index("ix_module_catalog_brand", "module_catalog", ["brand"])
        op.create_index("ix_module_catalog_name", "module_catalog", ["name"])
        op.create_index("ix_module_catalog_hp", "module_catalog", ["hp"])
        op.create_index("ix_module_catalog_category", "module_catalog", ["category"])
        op.create_index(
            "ix_module_catalog_is_available", "module_catalog", ["is_available"]
        )
        op.create_index("ix_module_catalog_source", "module_catalog", ["source"])
        op.create_index("idx_catalog_brand_name", "module_catalog", ["brand", "name"])
        op.create_index(
            "idx_catalog_category_hp", "module_catalog", ["category", "hp"]
        )
        op.create_index("idx_catalog_available", "module_catalog", ["is_available"])
        return

    cols = _column_names("module_catalog")
    if "source" not in cols:
        op.add_column(
            "module_catalog",
            sa.Column("source", sa.String(length=50), nullable=True),
        )
    # Index may be missing even if column was added manually.
    existing_indexes = {
        ix["name"] for ix in inspect(op.get_bind()).get_indexes("module_catalog")
    }
    if "ix_module_catalog_source" not in existing_indexes:
        op.create_index("ix_module_catalog_source", "module_catalog", ["source"])

    op.execute(
        "UPDATE module_catalog SET source = 'SynthCatalogResearch' "
        "WHERE source IS NULL"
    )


def downgrade() -> None:
    tables = _table_names()
    if "module_catalog" not in tables:
        return
    cols = _column_names("module_catalog")
    # Only drop the column we added — do not drop the whole table
    # (it may pre-exist outside Alembic on long-lived DBs).
    if "source" in cols:
        existing_indexes = {
            ix["name"] for ix in inspect(op.get_bind()).get_indexes("module_catalog")
        }
        if "ix_module_catalog_source" in existing_indexes:
            op.drop_index("ix_module_catalog_source", table_name="module_catalog")
        op.drop_column("module_catalog", "source")
