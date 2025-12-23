"""API endpoint tests for account dashboard endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from account.models import CreditLedgerEntry, Referral
from community.models import User
from core import create_access_token
from main import app


@pytest.fixture
def client(db_session: Session):
    """Create a test client with database override."""
    from core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"user_id": user.id, "username": user.username})
    return {"Authorization": f"Bearer {token}"}


def test_credits_balance_from_ledger(client: TestClient, db_session: Session, sample_user: User):
    """Credits balance should reflect ledger sum."""
    entries = [
        CreditLedgerEntry(user_id=sample_user.id, entry_type="Purchase", amount=10),
        CreditLedgerEntry(user_id=sample_user.id, entry_type="Spend", amount=-4),
    ]
    db_session.add_all(entries)
    db_session.commit()

    response = client.get("/api/me/credits", headers=auth_headers(sample_user))

    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 6
    assert len(data["entries"]) == 2


def test_credits_requires_auth(client: TestClient):
    """Credits endpoint should require auth."""
    response = client.get("/api/me/credits")
    assert response.status_code == 401


def test_referral_summary_counts(client: TestClient, db_session: Session, sample_user: User):
    """Referral summary should return pending and earned counts."""
    referred_pending = User(
        username="pendinguser",
        email="pending@example.com",
        password_hash="$2b$12$dummyhash",
    )
    referred_earned = User(
        username="earneduser",
        email="earned@example.com",
        password_hash="$2b$12$dummyhash",
    )
    db_session.add_all([referred_pending, referred_earned])
    db_session.commit()

    sample_user.referral_code = "REFCODE"
    db_session.commit()

    referrals = [
        Referral(
            referrer_user_id=sample_user.id,
            referred_user_id=referred_pending.id,
            status="pending",
        ),
        Referral(
            referrer_user_id=sample_user.id,
            referred_user_id=referred_earned.id,
            status="earned",
        ),
    ]
    db_session.add_all(referrals)
    db_session.commit()

    response = client.get("/api/me/referrals", headers=auth_headers(sample_user))

    assert response.status_code == 200
    data = response.json()
    assert data["referral_code"] == "REFCODE"
    assert data["pending_count"] == 1
    assert data["earned_count"] == 1
    assert len(data["recent_referrals"]) == 2


def test_referral_link_stable(client: TestClient, db_session: Session, sample_user: User):
    """Referral link should be stable for a user."""
    sample_user.referral_code = "STABLECODE"
    db_session.commit()

    response = client.get("/api/me/referrals", headers=auth_headers(sample_user))
    assert response.status_code == 200
    data = response.json()
    assert data["referral_code"] == "STABLECODE"
    assert "STABLECODE" in data["referral_link"]
