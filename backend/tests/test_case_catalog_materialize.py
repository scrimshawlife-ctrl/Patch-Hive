"""Tests for catalog → legacy Case materialization bridge."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from cases.models import Case
from core.database import get_db
from integrations.case_catalog_populator import import_records
from main import app


def _record() -> dict:
    return {
        "manufacturer": "Bridge Co",
        "model": "Eurorack 104",
        "format_family": "eurorack",
        "production_status": "available",
        "powered": True,
        "revision": {
            "revision_key": "research-2026",
            "row_count": 2,
            "capacity_value": 208,
            "capacity_unit": "hp",
            "depth_min_mm": 42,
            "confidence": "medium",
        },
        "rows": [
            {
                "row_index": 0,
                "format_family": "eurorack",
                "capacity_value": 104,
                "capacity_unit": "hp",
            },
            {
                "row_index": 1,
                "format_family": "eurorack",
                "capacity_value": 104,
                "capacity_unit": "hp",
            },
        ],
        "power_systems": [
            {
                "name": "primary",
                "connector_count": 16,
                "current_pos12_ma": 2000,
                "current_neg12_ma": 1200,
                "current_pos5_ma": 500,
            }
        ],
        "features": [],
        "sources": [],
        "prices": [],
    }


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seeded(db_session: Session) -> None:
    receipt = import_records(db_session, [_record()])
    assert receipt["inserted"] == 1


def test_materialize_creates_and_is_idempotent(client: TestClient, db_session: Session, seeded: None) -> None:
    first = client.post("/api/cases/catalog/bridge-co-eurorack-104/materialize")
    assert first.status_code == 200
    body = first.json()
    assert body["created"] is True
    assert body["case"]["brand"] == "Bridge Co"
    assert body["case"]["name"] == "Eurorack 104"
    assert body["case"]["total_hp"] == 208
    assert body["case"]["rows"] == 2
    assert body["case"]["hp_per_row"] == [104, 104]
    assert body["case"]["power_12v_ma"] == 2000
    assert body["case"]["meta"]["catalog_slug"] == "bridge-co-eurorack-104"
    case_id = body["case"]["id"]

    second = client.post("/api/cases/catalog/bridge-co-eurorack-104/materialize")
    assert second.status_code == 200
    assert second.json()["created"] is False
    assert second.json()["case"]["id"] == case_id
    assert db_session.query(Case).count() == 1


def test_materialize_missing(client: TestClient) -> None:
    resp = client.post("/api/cases/catalog/no-such-case/materialize")
    assert resp.status_code == 404


def test_rematerialize_preserves_enriched_rails_when_catalog_rails_null(
    client: TestClient, db_session: Session, seeded: None
) -> None:
    """Catalog null rails must not wipe known legacy capacities on rematerialize.

    Trigger: enrich a materialized case's rails, then re-import the catalog row
    with unspecified (null) rail currents and rematerialize. Power-budget
    enforcement depends on those integers remaining set.
    """
    from cases.models import CaseCatalog, CasePowerSystem, CaseRevision

    first = client.post("/api/cases/catalog/bridge-co-eurorack-104/materialize")
    assert first.status_code == 200
    case_id = first.json()["case"]["id"]

    legacy = db_session.query(Case).filter(Case.id == case_id).one()
    legacy.power_12v_ma = 2500
    legacy.power_neg12v_ma = 1500
    legacy.power_5v_ma = 800
    db_session.add(legacy)
    db_session.commit()

    catalog = (
        db_session.query(CaseCatalog)
        .filter(CaseCatalog.slug == "bridge-co-eurorack-104")
        .one()
    )
    revision = (
        db_session.query(CaseRevision)
        .filter(CaseRevision.case_id == catalog.id)
        .one()
    )
    power = (
        db_session.query(CasePowerSystem)
        .filter(CasePowerSystem.revision_id == revision.id, CasePowerSystem.name == "primary")
        .one()
    )
    power.current_pos12_ma = None
    power.current_neg12_ma = None
    power.current_pos5_ma = None
    db_session.add(power)
    db_session.commit()

    second = client.post("/api/cases/catalog/bridge-co-eurorack-104/materialize")
    assert second.status_code == 200
    body = second.json()
    assert body["created"] is False
    assert body["case"]["power_12v_ma"] == 2500
    assert body["case"]["power_neg12v_ma"] == 1500
    assert body["case"]["power_5v_ma"] == 800

    db_session.refresh(legacy)
    assert legacy.power_12v_ma == 2500
    assert legacy.power_neg12v_ma == 1500
    assert legacy.power_5v_ma == 800


def test_materialize_rejects_identity_only_revision_without_inventing_hp(
    client: TestClient, db_session: Session
) -> None:
    """Identity-only catalog revisions must fail closed (no 1HP stub invent)."""
    receipt = import_records(
        db_session,
        [
            {
                "manufacturer": "Stub Co",
                "model": "Identity Only",
                "format_family": "eurorack",
                "production_status": "unknown",
                "powered": True,
                "revision": {
                    "revision_key": "identity-only",
                    "row_count": None,
                    "capacity_value": None,
                    "capacity_unit": "hp",
                    "confidence": "low",
                },
                "rows": [],
                "power_systems": [],
                "features": [],
                "sources": [],
                "prices": [],
            }
        ],
    )
    assert receipt["inserted"] == 1

    # Pre-existing enriched legacy row with same brand/name must stay intact.
    prior = Case(
        brand="Stub Co",
        name="Identity Only",
        total_hp=84,
        rows=1,
        hp_per_row=[84],
        power_12v_ma=1000,
        source="ResearchCSV",
        source_reference="fixture",
    )
    db_session.add(prior)
    db_session.commit()
    prior_id = prior.id

    resp = client.post("/api/cases/catalog/stub-co-identity-only/materialize")
    assert resp.status_code == 400

    kept = db_session.query(Case).filter(Case.id == prior_id).one()
    assert kept.total_hp == 84
    assert kept.hp_per_row == [84]
    assert kept.power_12v_ma == 1000
