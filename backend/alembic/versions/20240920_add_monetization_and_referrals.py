"""Add monetization tables and referral fields.

Revision ID: 20240920_add_monetization_and_referrals
Revises:
Create Date: 2024-09-20 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "20240920_add_monetization_and_referrals"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("referral_code", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("referred_by", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE users SET referral_code = substr(md5(CAST(id AS text) || email), 1, 10) "
        "WHERE referral_code IS NULL"
    )
    op.alter_column("users", "referral_code", nullable=False)
    op.create_index("ix_users_referral_code", "users", ["referral_code"], unique=True)
    op.create_index("ix_users_referred_by", "users", ["referred_by"], unique=False)
    op.create_foreign_key(
        "fk_users_referred_by",
        "users",
        "users",
        ["referred_by"],
        ["id"],
    )

    op.create_table(
        "licenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("license_key", sa.String(length=100), nullable=False),
        sa.Column("terms_version", sa.String(length=50), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("license_key"),
    )

    op.create_table(
        "exports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("patch_id", sa.Integer(), nullable=True),
        sa.Column("rack_id", sa.Integer(), nullable=True),
        sa.Column("export_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("credits_spent", sa.Integer(), nullable=False),
        sa.Column("manifest_hash", sa.String(length=64), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
        sa.Column("license_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patch_id"], ["patches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rack_id"], ["racks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["license_id"], ["licenses.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_exports_manifest_hash", "exports", ["manifest_hash"], unique=False)
    op.create_index("ix_exports_patch_id", "exports", ["patch_id"], unique=False)
    op.create_index("ix_exports_rack_id", "exports", ["rack_id"], unique=False)
    op.create_index("ix_exports_user_id", "exports", ["user_id"], unique=False)

    op.create_table(
        "referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referrer_user_id", sa.Integer(), nullable=False),
        sa.Column("referred_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("first_purchase_id", sa.Integer(), nullable=True),
        sa.Column("rewarded_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["referrer_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referred_user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_referrals_referrer_user_id", "referrals", ["referrer_user_id"], unique=False
    )
    op.create_index(
        "ix_referrals_referred_user_id", "referrals", ["referred_user_id"], unique=False
    )
    op.create_unique_constraint("unique_referral_referred_user", "referrals", ["referred_user_id"])
    op.create_unique_constraint(
        "unique_referrer_referred_pair", "referrals", ["referrer_user_id", "referred_user_id"]
    )

    op.create_table(
        "credits_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=30), nullable=False),
        sa.Column("credits_delta", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("referral_id", sa.Integer(), nullable=True),
        sa.Column("export_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referral_id"], ["referrals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["export_id"], ["exports.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_credits_ledger_user_id", "credits_ledger", ["user_id"], unique=False)
    op.create_index(
        "ix_credits_ledger_change_type", "credits_ledger", ["change_type"], unique=False
    )
    op.create_index("ix_credits_ledger_export_id", "credits_ledger", ["export_id"], unique=False)
    op.create_index(
        "ix_credits_ledger_referral_id", "credits_ledger", ["referral_id"], unique=False
    )

    op.create_foreign_key(
        "fk_referrals_first_purchase",
        "referrals",
        "credits_ledger",
        ["first_purchase_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_referrals_first_purchase", "referrals", type_="foreignkey")
    op.drop_index("ix_credits_ledger_referral_id", table_name="credits_ledger")
    op.drop_index("ix_credits_ledger_export_id", table_name="credits_ledger")
    op.drop_index("ix_credits_ledger_change_type", table_name="credits_ledger")
    op.drop_index("ix_credits_ledger_user_id", table_name="credits_ledger")
    op.drop_table("credits_ledger")

    op.drop_constraint("unique_referrer_referred_pair", "referrals", type_="unique")
    op.drop_constraint("unique_referral_referred_user", "referrals", type_="unique")
    op.drop_index("ix_referrals_referred_user_id", table_name="referrals")
    op.drop_index("ix_referrals_referrer_user_id", table_name="referrals")
    op.drop_table("referrals")

    op.drop_index("ix_exports_user_id", table_name="exports")
    op.drop_index("ix_exports_rack_id", table_name="exports")
    op.drop_index("ix_exports_patch_id", table_name="exports")
    op.drop_index("ix_exports_manifest_hash", table_name="exports")
    op.drop_table("exports")

    op.drop_table("licenses")

    op.drop_constraint("fk_users_referred_by", "users", type_="foreignkey")
    op.drop_index("ix_users_referred_by", table_name="users")
    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_column("users", "referred_by")
    op.drop_column("users", "referral_code")
