"""Design pack artifact download after token issue."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from canon.exports import request_export
from canon.contracts import ExportRequest
from canon.fulfillment import fulfill_export
from canon.models import CanonicalCreditLedgerEntryRecord
from cases.models import Case
from community.models import User
from modules.models import Module
from patches.models import Patch
from racks.models import Rack, RackModule
from runs.bridge import ensure_legacy_run_export_bridge
from runs.models import Run
from fastapi.testclient import TestClient

from core import create_access_token
from main import app

NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _auth_headers(user: User) -> dict[str, str]:
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


def _seed(db: Session, tmp_path: Path, monkeypatch):
    import core.config as config_mod

    monkeypatch.setattr(config_mod.settings, "export_store_root", str(tmp_path))
    monkeypatch.setattr(config_mod.settings, "export_dir", str(tmp_path))
    monkeypatch.setattr(config_mod.settings, "enable_canon_export_fulfillment", True)
    monkeypatch.setattr(config_mod.settings, "enable_inline_export_fulfillment", False)
    # download secret must be long enough
    monkeypatch.setattr(config_mod.settings, "download_token_secret", "x" * 40)
    monkeypatch.setattr(config_mod.settings, "secret_key", "y" * 40)

    user = User(username="dl-user", email="dl@example.com", password_hash="h")
    case = Case(brand="PH", name="C", total_hp=84, rows=1, hp_per_row=[84], source="test")
    db.add_all([user, case])
    db.flush()
    rack = Rack(name="R", user_id=user.id, case_id=case.id)
    db.add(rack)
    db.flush()
    m1 = Module(brand="T", name="A", hp=12, module_type="VCO", source="test")
    m2 = Module(brand="T", name="B", hp=8, module_type="VCA", source="test")
    db.add_all([m1, m2])
    db.flush()
    db.add_all(
        [
            RackModule(rack_id=rack.id, module_id=m1.id, row_index=0, start_hp=0),
            RackModule(rack_id=rack.id, module_id=m2.id, row_index=0, start_hp=12),
        ]
    )
    run = Run(rack_id=rack.id, status="completed")
    db.add(run)
    db.flush()
    db.add(
        Patch(
            rack_id=rack.id,
            run_id=run.id,
            name="DL Patch",
            category="Voice",
            description="d",
            connections=[
                {
                    "from_module_id": m1.id,
                    "from_port": "Out",
                    "to_module_id": m2.id,
                    "to_port": "In",
                    "cable_type": "audio",
                }
            ],
            generation_seed=1,
            generation_version="1.0.0",
        )
    )
    db.flush()
    bridge = ensure_legacy_run_export_bridge(db, run)
    db.add(
        CanonicalCreditLedgerEntryRecord(
            id="ledger-grant-dl",
            user_id=user.id,
            delta=10,
            entry_type="grant",
            idempotency_key="grant-dl",
            export_id=None,
            created_at=NOW,
        )
    )
    db.commit()
    return user, bridge


def test_download_pdf_and_zip_after_fulfill(
    db_session: Session, tmp_path: Path, monkeypatch
) -> None:
    user, bridge = _seed(db_session, tmp_path, monkeypatch)
    export = request_export(
        db_session,
        ExportRequest(
            request_id="req-dl",
            user_id=user.id,
            source_run_id=bridge.source_run_id,
            source_rig_revision_id=bridge.rig_revision_id,
            formats=("pdf", "json"),
            license="personal",
            credit_cost=3,
            idempotency_key="idem-dl-1",
            requested_at=NOW,
        ),
        artifact_manifest_hash=bridge.artifact_manifest_hash,
        export_version="1.0.0",
    )
    db_session.commit()
    result = fulfill_export(db_session, export.id)
    db_session.commit()
    assert result.status == "succeeded"

    client = _client(db_session)
    token_resp = client.post(
        f"/api/canon/exports/{export.id}/download-token",
        headers=_auth_headers(user),
        json={"ttl_seconds": 120},
    )
    assert token_resp.status_code == 200, token_resp.text
    token = token_resp.json()["token"]

    pdf = client.get(
        f"/api/canon/exports/{export.id}/artifacts/pdf",
        headers=_auth_headers(user),
        params={"token": token},
    )
    assert pdf.status_code == 200, pdf.text
    assert pdf.content.startswith(b"%PDF")

    z = client.get(
        f"/api/canon/exports/{export.id}/artifacts/zip",
        headers=_auth_headers(user),
        params={"token": token},
    )
    assert z.status_code == 200
    assert z.headers["content-type"].startswith("application/zip")
    assert len(z.content) > 100

    # Bad token rejected
    bad = client.get(
        f"/api/canon/exports/{export.id}/artifacts/pdf",
        headers=_auth_headers(user),
        params={"token": "v1." + "bad" * 20},
    )
    assert bad.status_code in {403, 400}
