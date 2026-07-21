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
