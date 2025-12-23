"""
FastAPI routes for monetization events.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from community.models import User
from community.routes import require_auth
from core import get_db
from monetization.credits import get_credits_balance
from monetization.referrals import record_purchase
from monetization.schemas import PurchaseCreate

router = APIRouter()


@router.post("/purchases", status_code=201)
def create_purchase(
    purchase: PurchaseCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Record a paid purchase event for referral eligibility."""
    record_purchase(
        db,
        user=current_user,
        credits_delta=purchase.credits_delta,
        notes=purchase.notes,
    )
    db.commit()
    return {"status": "recorded"}


@router.get("/credits/balance")
def get_balance(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Get the current user's credits balance."""
    balance = get_credits_balance(db, current_user.id)
    return {"balance": balance}
