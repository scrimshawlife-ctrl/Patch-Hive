"""Allow append-only referrals by removing uniqueness constraints.

Revision ID: 20240921_make_referrals_append_only
Revises: 20240920_add_monetization_and_referrals
Create Date: 2024-09-21 00:00:00.000000
"""
from alembic import op


revision = "20240921_make_referrals_append_only"
down_revision = "20240920_add_monetization_and_referrals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("unique_referrer_referred_pair", "referrals", type_="unique")
    op.drop_constraint("unique_referral_referred_user", "referrals", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "unique_referral_referred_user", "referrals", ["referred_user_id"]
    )
    op.create_unique_constraint(
        "unique_referrer_referred_pair", "referrals", ["referrer_user_id", "referred_user_id"]
    )
