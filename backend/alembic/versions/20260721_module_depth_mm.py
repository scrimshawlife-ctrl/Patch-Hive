"""Optional module depth for catalog physical-fit checks.

Revision ID: 20260721_module_depth_mm
Revises: 20260721_case_format_columns
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260721_module_depth_mm"
down_revision = "20260721_case_format_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("modules", sa.Column("depth_mm", sa.Float(), nullable=True))
    op.create_index("ix_modules_depth_mm", "modules", ["depth_mm"])


def downgrade() -> None:
    op.drop_index("ix_modules_depth_mm", table_name="modules")
    op.drop_column("modules", "depth_mm")
