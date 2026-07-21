"""Matrix slice A: generate ensures export bridge without relying on run list GET."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from canon.models import GenerationRunRecord, PatchLibraryRecord, RigRevisionRecord
from main import app
from racks.models import Rack
from runs.bridge import legacy_source_run_id


def _client(db_session: Session) -> TestClient:
    from core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_generate_patches_ensures_export_bridge(
    db_session: Session, sample_rack_basic: Rack
) -> None:
    client = _client(db_session)
    resp = client.post(f"/api/patches/generate/{sample_rack_basic.id}", json={})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["run_id"] is not None
    assert body["export_bridge_ready"] is True
    assert body["source_run_id"] == legacy_source_run_id(int(body["run_id"]))
    assert body["rig_revision_id"] == f"legacy-rack-{sample_rack_basic.id}"
    assert body["artifact_manifest_hash"] and len(body["artifact_manifest_hash"]) == 64

    assert db_session.get(RigRevisionRecord, body["rig_revision_id"]) is not None
    rev = db_session.get(RigRevisionRecord, body["rig_revision_id"])
    assert rev is not None
    assert rev.canonical_rig.get("schema") == "patchhive.rack-snapshot.v1"
    assert isinstance(rev.canonical_rig.get("modules"), list)
    assert len(str(rev.canonical_hash)) == 64
    assert db_session.get(GenerationRunRecord, body["source_run_id"]) is not None
    assert db_session.get(PatchLibraryRecord, f"library-{body['source_run_id']}") is not None

    # List runs still ready without additional invent
    listed = client.get(f"/api/runs?rack_id={sample_rack_basic.id}")
    assert listed.status_code == 200
    run_row = next(r for r in listed.json()["runs"] if r["id"] == body["run_id"])
    assert run_row["export_bridge_ready"] is True
    assert run_row["source_run_id"] == body["source_run_id"]

    app.dependency_overrides.clear()
