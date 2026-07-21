"""API tests for the normalized modular case catalog read surface."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.database import get_db
from integrations.case_catalog_populator import import_records
from main import app


def _seed_record(
    *,
    manufacturer: str = "Test Instruments",
    model: str = "Travel 84",
    format_family: str = "eurorack",
    capacity_value: float = 84,
    capacity_unit: str = "hp",
    powered: bool = True,
    portable: bool = True,
    pos12: int = 1500,
    depth_max_mm: float = 55,
    feature_key: str = "removable_lid",
) -> dict:
    return {
        "manufacturer": manufacturer,
        "model": model,
        "format_family": format_family,
        "production_status": "available",
        "powered": powered,
        "official_url": f"https://example.com/{model.lower().replace(' ', '-')}",
        "revision": {
            "revision_key": "research-2026",
            "revision_label": "Research",
            "row_count": 1,
            "capacity_value": capacity_value,
            "capacity_unit": capacity_unit,
            "depth_max_mm": depth_max_mm,
            "portable": portable,
            "removable_lid": True,
            "confidence": "medium",
        },
        "rows": [
            {
                "row_index": 0,
                "format_family": format_family,
                "capacity_value": capacity_value,
                "capacity_unit": capacity_unit,
                "depth_max_mm": depth_max_mm,
            }
        ],
        "power_systems": [
            {
                "name": "primary",
                "supply_type": "external_brick",
                "connector_count": 12,
                "current_pos12_ma": pos12 if powered else None,
                "current_neg12_ma": 1000 if powered else None,
                "current_pos5_ma": 500 if powered else None,
            }
        ],
        "features": [
            {
                "feature_key": feature_key,
                "feature_value": "yes",
                "verified": False,
            }
        ],
        "sources": [
            {
                "source_type": "research_synthesis",
                "title": "Unit test source",
                "url": "https://example.com/research",
                "field_path": "revision.capacity_value",
                "published_value": str(capacity_value),
                "normalized_value": str(capacity_value),
                "confidence": "medium",
                "policy": {
                    "access_basis": "manual_research",
                    "license_status": "research_synthesis",
                    "evidence_status": "UNKNOWN",
                    "review_state": "pending",
                    "observed_at": "2026-07-21T00:00:00Z",
                    "retrieved_at": "2026-07-21T12:00:00Z",
                    "content_hash": "b" * 64,
                    "normalizer_version": "case-catalog-v1",
                },
            }
        ],
        "prices": [
            {
                "source_name": "Test Dealer",
                "source_url": "https://example.com/store",
                "amount": "399.00",
                "currency": "USD",
                "price_type": "street",
                "captured_at": "2026-07-21T12:00:00Z",
            }
        ],
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
def seeded_catalog(db_session: Session) -> None:
    records = [
        _seed_record(model="Travel 84", capacity_value=84, pos12=1500, portable=True),
        _seed_record(
            manufacturer="Boat Works",
            model="Panel Four",
            format_family="buchla_200",
            capacity_value=4,
            capacity_unit="buchla_panel",
            powered=True,
            portable=False,
            pos12=None,
            depth_max_mm=None,
            feature_key="format_raw",
        ),
        _seed_record(
            manufacturer="Skiff Co",
            model="Passive 104",
            capacity_value=104,
            powered=False,
            portable=True,
            pos12=0,
            depth_max_mm=40,
        ),
    ]
    # Fix passive / buchla edge fields for honest null rails
    records[1]["power_systems"] = [
        {
            "name": "primary",
            "supply_type": "integrated",
            "current_pos12_ma": None,
            "current_neg12_ma": None,
            "current_pos5_ma": None,
        }
    ]
    records[1]["revision"]["depth_max_mm"] = None
    records[2]["power_systems"] = [
        {
            "name": "primary",
            "supply_type": "none",
            "current_pos12_ma": None,
            "current_neg12_ma": None,
            "current_pos5_ma": None,
        }
    ]
    receipt = import_records(db_session, records)
    assert receipt["rejected"] == 0
    assert receipt["inserted"] == 3


def test_list_catalog_and_filters(client: TestClient, seeded_catalog: None) -> None:
    all_resp = client.get("/api/cases/catalog")
    assert all_resp.status_code == 200
    body = all_resp.json()
    assert body["total"] == 3
    assert len(body["cases"]) == 3
    assert body["cases"][0]["slug"]

    eurorack = client.get("/api/cases/catalog", params={"format_family": "eurorack"})
    assert eurorack.status_code == 200
    assert eurorack.json()["total"] == 2

    powered = client.get("/api/cases/catalog", params={"powered": True, "min_capacity": 80})
    assert powered.status_code == 200
    assert powered.json()["total"] == 1
    assert powered.json()["cases"][0]["model"] == "Travel 84"

    depth = client.get("/api/cases/catalog", params={"min_depth_mm": 50})
    assert depth.status_code == 200
    assert depth.json()["total"] == 1

    rails = client.get("/api/cases/catalog", params={"min_pos12_ma": 1000})
    assert rails.status_code == 200
    assert rails.json()["total"] == 1

    search = client.get("/api/cases/catalog", params={"q": "boat"})
    assert search.status_code == 200
    assert search.json()["total"] == 1
    assert search.json()["cases"][0]["format_family"] == "buchla_200"


def test_catalog_detail_includes_policy(client: TestClient, seeded_catalog: None) -> None:
    resp = client.get("/api/cases/catalog/test-instruments-travel-84")
    assert resp.status_code == 200
    body = resp.json()
    assert body["manufacturer"] == "Test Instruments"
    assert body["revisions"]
    assert body["revisions"][0]["capacity_unit"] == "hp"
    assert body["revisions"][0]["rows"]
    assert body["revisions"][0]["power_systems"]
    assert body["sources"]
    assert body["sources"][0]["policy"]["access_basis"] == "manual_research"
    assert body["prices"]

    missing = client.get("/api/cases/catalog/does-not-exist")
    assert missing.status_code == 404


def test_catalog_revisions_manufacturers_formats_stats(
    client: TestClient, seeded_catalog: None
) -> None:
    revs = client.get("/api/cases/catalog/test-instruments-travel-84/revisions")
    assert revs.status_code == 200
    assert len(revs.json()["revisions"]) == 1

    mfr = client.get("/api/cases/catalog/manufacturers")
    assert mfr.status_code == 200
    names = {row["name"] for row in mfr.json()["manufacturers"]}
    assert "Test Instruments" in names
    assert "Boat Works" in names

    formats = client.get("/api/cases/catalog/formats")
    assert formats.status_code == 200
    families = {row["format_family"] for row in formats.json()["formats"]}
    assert "eurorack" in families
    assert "buchla_200" in families

    stats = client.get("/api/cases/catalog/stats")
    assert stats.status_code == 200
    body = stats.json()
    assert body["case_count"] == 3
    assert body["manufacturer_count"] == 3
    assert body["with_sources"] == 3
    assert body["source_packet_count"] >= 3
    assert body["format_family_counts"]["eurorack"] == 2


def test_legacy_case_routes_still_resolve(client: TestClient, db_session: Session) -> None:
    """Integer case_id routes must not be shadowed by /catalog."""
    from cases.models import Case

    legacy = Case(
        brand="Legacy",
        name="84HP",
        total_hp=84,
        rows=1,
        hp_per_row=[84],
        format_family="Eurorack",
        capacity_unit="hp",
        powered=True,
        source="test",
    )
    db_session.add(legacy)
    db_session.commit()
    db_session.refresh(legacy)

    resp = client.get(f"/api/cases/{legacy.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "84HP"

    catalog = client.get("/api/cases/catalog")
    assert catalog.status_code == 200
