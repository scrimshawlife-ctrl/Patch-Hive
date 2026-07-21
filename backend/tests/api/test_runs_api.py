"""API tests for run list bridge fields."""

from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from cases.models import Case
from community.models import User
from main import app
from racks.models import Rack
from runs.bridge import legacy_artifact_manifest_hash, legacy_rig_revision_id, legacy_source_run_id
from runs.models import Run
from canon.models import GenerationRunRecord, PatchLibraryRecord, RigRevisionRecord


def _client(db_session: Session) -> TestClient:
    from core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _seed_run(db_session: Session) -> Run:
    user = User(username="run-user", email="run@example.com", password_hash="hash")
    case = Case(
        brand="PatchHive",
        name="Case",
        total_hp=84,
        rows=1,
        hp_per_row=[84],
        source="test",
    )
    db_session.add_all((user, case))
    db_session.flush()
    rack = Rack(user_id=user.id, case_id=case.id, name="Rig")
    db_session.add(rack)
    db_session.flush()
    run = Run(rack_id=rack.id, status="completed", created_at=datetime.utcnow())
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    return run


def test_list_runs_includes_export_bridge_and_ensures_canon_rows(db_session: Session) -> None:
    client = _client(db_session)
    run = _seed_run(db_session)

    resp = client.get(f"/api/runs?rack_id={run.rack_id}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] == 1
    row = body["runs"][0]
    assert row["id"] == run.id
    assert row["rack_id"] == run.rack_id
    assert row["rig_revision_id"] == legacy_rig_revision_id(int(run.rack_id))
    assert row["source_run_id"] == legacy_source_run_id(int(run.id))
    assert row["artifact_manifest_hash"] == legacy_artifact_manifest_hash(
        int(run.id), int(run.rack_id)
    )
    assert row["export_bridge_ready"] is True
    assert len(row["artifact_manifest_hash"]) == 64
    assert row.get("created_at")

    assert db_session.get(RigRevisionRecord, row["rig_revision_id"]) is not None
    assert db_session.get(GenerationRunRecord, row["source_run_id"]) is not None
    assert db_session.get(PatchLibraryRecord, f"library-{row['source_run_id']}") is not None

    # Idempotent second list
    resp2 = client.get(f"/api/runs?rack_id={run.rack_id}")
    assert resp2.status_code == 200
    assert resp2.json()["runs"][0]["source_run_id"] == row["source_run_id"]

    app.dependency_overrides.clear()


def test_get_run_bridge_matches_list(db_session: Session) -> None:
    client = _client(db_session)
    run = _seed_run(db_session)
    listed = client.get(f"/api/runs?rack_id={run.rack_id}").json()["runs"][0]
    got = client.get(f"/api/runs/{run.id}")
    assert got.status_code == 200
    body = got.json()
    assert body["source_run_id"] == listed["source_run_id"]
    assert body["rig_revision_id"] == listed["rig_revision_id"]
    assert body["artifact_manifest_hash"] == listed["artifact_manifest_hash"]
    app.dependency_overrides.clear()
