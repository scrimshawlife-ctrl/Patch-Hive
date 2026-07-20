"""Create social and account tables missing from the foundation chain.

Revision ID: 20240928_fix_schema_gaps
Revises: 20240927_canon_alignment
"""

import sqlalchemy as sa
from alembic import op

revision = "20240928_fix_schema_gaps"
down_revision = "20240927_canon_alignment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rack_id", sa.Integer(), nullable=True),
        sa.Column("patch_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patch_id"], ["patches.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "rack_id", name="unique_user_rack_vote"),
        sa.UniqueConstraint("user_id", "patch_id", name="unique_user_patch_vote"),
    )
    op.create_index("ix_votes_id", "votes", ["id"])
    op.create_index("ix_votes_user_id", "votes", ["user_id"])
    op.create_index("ix_votes_rack_id", "votes", ["rack_id"])
    op.create_index("ix_votes_patch_id", "votes", ["patch_id"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rack_id", sa.Integer(), nullable=True),
        sa.Column("patch_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patch_id"], ["patches.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_comments_id", "comments", ["id"])
    op.create_index("ix_comments_user_id", "comments", ["user_id"])
    op.create_index("ix_comments_rack_id", "comments", ["rack_id"])
    op.create_index("ix_comments_patch_id", "comments", ["patch_id"])

    op.create_table(
        "credit_ledger_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_credit_ledger_entries_id", "credit_ledger_entries", ["id"])
    op.create_index("ix_credit_ledger_entries_user_id", "credit_ledger_entries", ["user_id"])

    op.create_table(
        "export_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("export_type", sa.String(length=20), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("unlocked", sa.Boolean(), nullable=False),
        sa.Column("license_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_export_records_id", "export_records", ["id"])
    op.create_index("ix_export_records_user_id", "export_records", ["user_id"])

    op.create_table(
        "account_referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referrer_user_id", sa.Integer(), nullable=False),
        sa.Column("referred_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("rewarded_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["referrer_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referred_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("referred_user_id", name="unique_account_referral_referred_user"),
        sa.UniqueConstraint(
            "referrer_user_id",
            "referred_user_id",
            name="unique_account_referrer_referred_pair",
        ),
    )
    op.create_index("ix_account_referrals_id", "account_referrals", ["id"])
    op.create_index(
        "ix_account_referrals_referrer_user_id", "account_referrals", ["referrer_user_id"]
    )
    op.create_index(
        "ix_account_referrals_referred_user_id", "account_referrals", ["referred_user_id"]
    )


def downgrade() -> None:
    for table in (
        "account_referrals",
        "export_records",
        "credit_ledger_entries",
        "comments",
        "votes",
    ):
        op.drop_table(table)
