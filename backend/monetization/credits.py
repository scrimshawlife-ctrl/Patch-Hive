"""Credits ledger helpers."""

from sqlalchemy.orm import Session

from monetization.models import CreditsLedger


def get_credits_balance(db: Session, user_id: int) -> int:
    entries = db.query(CreditsLedger).filter(CreditsLedger.user_id == user_id).all()
    return sum(entry.credits_delta for entry in entries)
