from sqlalchemy.orm import Session

from admin.models import AdminAuditLog, PendingFunction
from modules.models import Module


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_admin_audit_log_module_tombstone(
    api_client,
    db_session: Session,
    seed_minimal_modules,
    admin_user,
):
    admin_login = api_client.post(
        "/api/community/auth/login",
        json={"username": admin_user.username, "password": "admin-pass"},
    )
    admin_login.raise_for_status()
    admin_token = admin_login.json()["access_token"]

    module_id = seed_minimal_modules["modules"][0].id
    resp = api_client.patch(
        f"/api/admin/modules/{module_id}/status",
        json={"status": "tombstoned", "reason": "retired"},
        headers=_auth_headers(admin_token),
    )
    resp.raise_for_status()

    module = db_session.query(Module).filter(Module.id == module_id).first()
    assert module.status == "tombstoned"

    audit = (
        db_session.query(AdminAuditLog)
        .filter(AdminAuditLog.action_type == "module.status.update")
        .first()
    )
    assert audit
    assert audit.target_id == str(module_id)
    assert audit.reason == "retired"


def test_pending_function_review_queue(api_client, db_session: Session, admin_user):
    admin_login = api_client.post(
        "/api/community/auth/login",
        json={"username": admin_user.username, "password": "admin-pass"},
    )
    admin_login.raise_for_status()
    admin_token = admin_login.json()["access_token"]

    payload = {
        "brand": "Obscura",
        "name": "Mystery Jack",
        "hp": 8,
        "module_type": "UTIL",
        "io_ports": [{"name": "Mystery", "type": "proprietary_clock"}],
        "tags": ["utility"],
        "description": "Unknown function jack",
        "manufacturer_url": None,
        "source": "Manual",
        "source_reference": "acceptance",
    }
    create_resp = api_client.post(
        "/api/admin/modules",
        json=payload,
        headers=_auth_headers(admin_token),
    )
    create_resp.raise_for_status()

    pending = db_session.query(PendingFunction).first()
    assert pending
    assert pending.status == "pending"

    approve_resp = api_client.post(
        f"/api/admin/functions/{pending.id}/approve",
        json={"canonical_function": "clock_out", "reason": "reviewed"},
        headers=_auth_headers(admin_token),
    )
    approve_resp.raise_for_status()

    pending = db_session.query(PendingFunction).filter(PendingFunction.id == pending.id).first()
    assert pending.status == "approved"
    assert pending.canonical_function == "clock_out"

    audit = (
        db_session.query(AdminAuditLog)
        .filter(AdminAuditLog.action_type == "function.approve")
        .first()
    )
    assert audit


def test_non_admin_denied(api_client, create_user):
    user = create_user("member", "member-pass", role="User")
    login = api_client.post(
        "/api/community/auth/login",
        json={"username": user.username, "password": "member-pass"},
    )
    login.raise_for_status()
    token = login.json()["access_token"]

    resp = api_client.post(
        f"/api/admin/users/{user.id}/credits/grant",
        json={"credits": 1, "reason": "nope"},
        headers=_auth_headers(token),
    )
    assert resp.status_code == 403
