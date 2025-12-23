"""Service helpers for account operations."""

from __future__ import annotations

import secrets
from typing import Optional

from sqlalchemy.orm import Session

from community.models import User


def ensure_referral_code(db: Session, user: User) -> str:
    """Ensure a user has a stable referral code."""
    if user.referral_code:
        return user.referral_code

    referral_code = generate_referral_code(db)
    user.referral_code = referral_code
    db.commit()
    db.refresh(user)
    return referral_code


def generate_referral_code(db: Session, length: int = 10) -> str:
    """Generate a unique referral code."""
    while True:
        code = secrets.token_urlsafe(length)[:length].upper()
        existing = db.query(User).filter(User.referral_code == code).first()
        if not existing:
            return code


def mask_user_id(user_id: int) -> str:
    """Mask a user ID for referral summaries."""
    suffix = str(user_id)[-4:]
    return f"user-****{suffix}"


def build_referral_link(base_url: str, referral_code: str) -> str:
    """Build referral link for the frontend."""
    return f"{base_url.rstrip('/')}/signup?ref={referral_code}"
