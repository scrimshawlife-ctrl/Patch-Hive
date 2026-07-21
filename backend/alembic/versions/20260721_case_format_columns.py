"""Case format honesty: format_family, capacity_unit, powered.

Revision ID: 20260721_case_format_columns
Revises: 20260721_user_style_recipes
Create Date: 2026-07-21
"""

from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "20260721_case_format_columns"
down_revision = "20260721_user_style_recipes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("format_family", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "cases",
        sa.Column("capacity_unit", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "cases",
        sa.Column("powered", sa.Boolean(), nullable=True),
    )
    op.create_index("ix_cases_format_family", "cases", ["format_family"])
    op.create_index("ix_cases_capacity_unit", "cases", ["capacity_unit"])
    op.create_index("ix_cases_powered", "cases", ["powered"])

    # Backfill from meta JSON when present (dialect-portable via Python).
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, name, meta FROM cases")).fetchall()
    for row in rows:
        case_id, name, meta = row[0], row[1], row[2]
        data = meta
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = None
        if not isinstance(data, dict):
            data = {}
        family = (data.get("format_family") or "").strip() or "Eurorack"
        unit = (data.get("capacity_unit") or "").strip() or "hp"
        if "powered" in data:
            powered = bool(data.get("powered"))
        else:
            name_l = (name or "").lower()
            powered = "no power" not in name_l and "unpowered" not in name_l
        conn.execute(
            sa.text(
                "UPDATE cases SET format_family = :f, capacity_unit = :u, powered = :p WHERE id = :id"
            ),
            {"f": family, "u": unit, "p": powered, "id": case_id},
        )


def downgrade() -> None:
    op.drop_index("ix_cases_powered", table_name="cases")
    op.drop_index("ix_cases_capacity_unit", table_name="cases")
    op.drop_index("ix_cases_format_family", table_name="cases")
    op.drop_column("cases", "powered")
    op.drop_column("cases", "capacity_unit")
    op.drop_column("cases", "format_family")
