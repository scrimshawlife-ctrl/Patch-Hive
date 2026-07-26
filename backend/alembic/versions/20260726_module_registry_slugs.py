"""Add registry slug columns to modules and module_catalog.

Revision ID: 20260726_module_registry_slugs
Revises: 20260723_add_device_registry
Create Date: 2026-07-26

PDB wiring columns were added to SQLAlchemy models without an Alembic revision,
so postgres CI (alembic upgrade head) lacked modules.registry_* columns used by
acceptance and materialize paths.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260726_module_registry_slugs"
down_revision = "20260723_add_device_registry"
branch_labels = None
depends_on = None


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    if table not in set(inspect(bind).get_table_names()):
        return set()
    return {c["name"] for c in inspect(bind).get_columns(table)}


def _indexes(table: str) -> set[str]:
    bind = op.get_bind()
    if table not in set(inspect(bind).get_table_names()):
        return set()
    return {ix["name"] for ix in inspect(bind).get_indexes(table)}


def _add_registry_slugs(table: str) -> None:
    cols = _column_names(table)
    if not cols:
        return
    if "registry_manufacturer_slug" not in cols:
        op.add_column(
            table,
            sa.Column("registry_manufacturer_slug", sa.String(length=100), nullable=True),
        )
    if "registry_device_slug" not in cols:
        op.add_column(
            table,
            sa.Column("registry_device_slug", sa.String(length=200), nullable=True),
        )
    idxs = _indexes(table)
    man_idx = f"ix_{table}_registry_manufacturer_slug"
    dev_idx = f"ix_{table}_registry_device_slug"
    if man_idx not in idxs:
        op.create_index(man_idx, table, ["registry_manufacturer_slug"])
    if dev_idx not in idxs:
        op.create_index(dev_idx, table, ["registry_device_slug"])


def upgrade() -> None:
    _add_registry_slugs("modules")
    _add_registry_slugs("module_catalog")


def downgrade() -> None:
    for table in ("module_catalog", "modules"):
        cols = _column_names(table)
        if not cols:
            continue
        idxs = _indexes(table)
        for name in (
            f"ix_{table}_registry_device_slug",
            f"ix_{table}_registry_manufacturer_slug",
        ):
            if name in idxs:
                op.drop_index(name, table_name=table)
        if "registry_device_slug" in cols:
            op.drop_column(table, "registry_device_slug")
        if "registry_manufacturer_slug" in cols:
            op.drop_column(table, "registry_manufacturer_slug")
