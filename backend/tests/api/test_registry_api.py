"""API tests for Product Database registry endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.database import get_db
from main import app
from registry.models import DeviceModel, Manufacturer


@pytest.fixture
def client(db_session: Session):
    manufacturer = Manufacturer(
        slug="test-instruments",
        canonical_name="Test Instruments",
        status="active",
        provenance={"source": "test"},
    )
    db_session.add(manufacturer)
    db_session.flush()
    db_session.add(
        DeviceModel(
            manufacturer_id=manufacturer.id,
            slug="math-test",
            canonical_name="Math Test",
            device_type="module",
            format="eurorack",
            hp=12,
            provenance={"source": "test"},
        )
    )
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_registry_manufacturers_endpoint(client: TestClient):
    response = client.get("/api/registry/manufacturers?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"] == [
        {
            "id": data["items"][0]["id"],
            "slug": "test-instruments",
            "name": "Test Instruments",
            "model_count": 1,
            "status": "active",
        }
    ]


def test_registry_search_endpoint(client: TestClient):
    response = client.get("/api/registry/search?q=maths&limit=3")
    assert response.status_code == 200
    assert "results" in response.json()


def test_registry_coverage_endpoint(client: TestClient):
    response = client.get("/api/registry/coverage")
    assert response.status_code == 200
    assert response.json() == {
        "total_manufacturers": 1,
        "total_models": 1,
        "hp_coverage_pct": 100.0,
    }
