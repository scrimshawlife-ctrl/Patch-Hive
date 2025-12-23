from pathlib import Path

from sqlalchemy.orm import Session

from monetization.models import CreditsLedger, Export


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_export_blocked_without_credits(api_client, db_session: Session, golden_demo_seed):
    login_resp = api_client.post(
        "/api/community/auth/login",
        json={"username": golden_demo_seed.username, "password": golden_demo_seed.password},
    )
    login_resp.raise_for_status()
    token = login_resp.json()["access_token"]

    resp = api_client.post(
        f"/api/export/runs/{golden_demo_seed.run_id}/patchbook",
        headers=_auth_headers(token),
    )
    assert resp.status_code in {402, 403}

    ledger_entries = (
        db_session.query(CreditsLedger)
        .filter(CreditsLedger.user_id == golden_demo_seed.user_id)
        .all()
    )
    exports = db_session.query(Export).filter(Export.run_id == golden_demo_seed.run_id).all()
    assert not ledger_entries
    assert not exports


def test_admin_grant_then_export_succeeds(
    api_client, db_session: Session, golden_demo_seed, admin_user
):
    admin_login = api_client.post(
        "/api/community/auth/login",
        json={"username": admin_user.username, "password": "admin-pass"},
    )
    admin_login.raise_for_status()
    admin_token = admin_login.json()["access_token"]

    grant = api_client.post(
        f"/api/admin/users/{golden_demo_seed.user_id}/credits/grant",
        json={"credits": 10, "reason": "acceptance"},
        headers=_auth_headers(admin_token),
    )
    grant.raise_for_status()

    ledger_entries = (
        db_session.query(CreditsLedger)
        .filter(CreditsLedger.user_id == golden_demo_seed.user_id)
        .all()
    )
    assert any(entry.change_type == "Grant" for entry in ledger_entries)

    login_resp = api_client.post(
        "/api/community/auth/login",
        json={"username": golden_demo_seed.username, "password": golden_demo_seed.password},
    )
    login_resp.raise_for_status()
    token = login_resp.json()["access_token"]

    export_resp = api_client.post(
        f"/api/export/runs/{golden_demo_seed.run_id}/patchbook",
        headers=_auth_headers(token),
    )
    export_resp.raise_for_status()
    data = export_resp.json()
    assert data["export_id"]
    assert data["artifact_path"]
    assert Path(data["artifact_path"]).exists()

    ledger_entries = (
        db_session.query(CreditsLedger)
        .filter(CreditsLedger.user_id == golden_demo_seed.user_id)
        .all()
    )
    assert any(entry.change_type == "Spend" for entry in ledger_entries)

    export_record = db_session.query(Export).filter(Export.id == data["export_id"]).first()
    assert export_record
    assert export_record.run_id == golden_demo_seed.run_id

    cached_resp = api_client.post(
        f"/api/export/runs/{golden_demo_seed.run_id}/patchbook",
        headers=_auth_headers(token),
    )
    cached_resp.raise_for_status()
    cached_data = cached_resp.json()
    assert cached_data["cached"] is True


def test_failed_export_does_not_consume_credits(
    api_client, db_session: Session, golden_demo_seed, admin_user
):
    admin_login = api_client.post(
        "/api/community/auth/login",
        json={"username": admin_user.username, "password": "admin-pass"},
    )
    admin_login.raise_for_status()
    admin_token = admin_login.json()["access_token"]

    api_client.post(
        f"/api/admin/users/{golden_demo_seed.user_id}/credits/grant",
        json={"credits": 5, "reason": "acceptance"},
        headers=_auth_headers(admin_token),
    )

    login_resp = api_client.post(
        "/api/community/auth/login",
        json={"username": golden_demo_seed.username, "password": golden_demo_seed.password},
    )
    login_resp.raise_for_status()
    token = login_resp.json()["access_token"]

    resp = api_client.post(
        f"/api/export/runs/{golden_demo_seed.run_id}/patchbook?force_fail=true",
        headers=_auth_headers(token),
    )
    assert resp.status_code == 500

    spends = (
        db_session.query(CreditsLedger)
        .filter(
            CreditsLedger.user_id == golden_demo_seed.user_id,
            CreditsLedger.change_type == "Spend",
        )
        .all()
    )
    assert not spends

    exports = db_session.query(Export).filter(Export.run_id == golden_demo_seed.run_id).all()
    assert not exports
