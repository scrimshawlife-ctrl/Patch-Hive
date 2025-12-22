"""
API endpoint tests for /api/admin.
"""
import pytest

pytest.importorskip("httpx", reason="httpx is required for FastAPI TestClient")

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.security import create_access_token
from main import app
from admin.models import AdminAuditLog
from community.models import User
from modules.models import Module
from monetization.models import CreditsLedger


def _create_user(db_session: Session, username: str, role: str) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        password_hash="hash",
        referral_code=f"{username}code",
        role=role,
        display_name=username.title(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers(user: User) -> dict:
    token = create_access_token({"user_id": user.id, "username": user.username})
    return {"Authorization": f"Bearer {token}"}


def _client(db_session: Session) -> TestClient:
    from core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_admin_requires_role(db_session: Session):
    client = _client(db_session)
    user = _create_user(db_session, "basic", "User")
    response = client.get("/api/admin/users", headers=_auth_headers(user))
    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_admin_grant_credits_writes_audit_log(db_session: Session):
    client = _client(db_session)
    admin = _create_user(db_session, "admin", "Admin")
    target = _create_user(db_session, "target", "User")

    response = client.post(
        f"/api/admin/users/{target.id}/credits/grant",
        json={"credits": 5, "reason": "manual grant"},
        headers=_auth_headers(admin),
    )
    assert response.status_code == 201

    ledger_entries = db_session.query(CreditsLedger).filter(CreditsLedger.user_id == target.id).all()
    assert len(ledger_entries) == 1
    assert ledger_entries[0].credits_delta == 5

    audit_entries = db_session.query(AdminAuditLog).filter(AdminAuditLog.action_type == "credits.grant").all()
    assert len(audit_entries) == 1
    assert audit_entries[0].reason == "manual grant"
    app.dependency_overrides.clear()


def test_module_tombstone_preserves_record(db_session: Session):
    client = _client(db_session)
    admin = _create_user(db_session, "ops", "Ops")

    module = Module(
        brand="Test",
        name="Tombstone",
        hp=8,
        module_type="VCO",
        io_ports=[],
        tags=[],
        source="Manual",
    )
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)

    response = client.patch(
        f"/api/admin/modules/{module.id}/status",
        json={"status": "tombstoned", "reason": "bad data"},
        headers=_auth_headers(admin),
    )
    assert response.status_code == 200

    db_session.refresh(module)
    assert module.status == "tombstoned"

    list_response = client.get("/api/modules")
    assert list_response.status_code == 200
    assert all(item["id"] != module.id for item in list_response.json()["modules"])
    app.dependency_overrides.clear()


def test_module_merge_does_not_delete(db_session: Session):
    client = _client(db_session)
    admin = _create_user(db_session, "admin2", "Admin")

    primary = Module(
        brand="Test",
        name="Primary",
        hp=8,
        module_type="VCO",
        io_ports=[],
        tags=[],
        source="Manual",
    )
    replacement = Module(
        brand="Test",
        name="Replacement",
        hp=8,
        module_type="VCO",
        io_ports=[],
        tags=[],
        source="Manual",
    )
    db_session.add_all([primary, replacement])
    db_session.commit()

    response = client.patch(
        f"/api/admin/modules/{primary.id}/merge",
        json={"replacement_module_id": replacement.id, "reason": "merge"},
        headers=_auth_headers(admin),
    )
    assert response.status_code == 200

    db_session.refresh(primary)
    assert primary.replacement_module_id == replacement.id
    assert db_session.query(Module).count() == 2
    app.dependency_overrides.clear()
