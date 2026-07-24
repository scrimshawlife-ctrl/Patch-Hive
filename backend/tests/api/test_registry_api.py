"""Basic API tests for the registry endpoints."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_registry_manufacturers_endpoint():
    response = client.get("/api/registry/manufacturers?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data or "total" in data


def test_registry_search_endpoint():
    response = client.get("/api/registry/search?q=maths&limit=3")
    assert response.status_code == 200
    assert "results" in response.json()


def test_registry_coverage_endpoint():
    response = client.get("/api/registry/coverage")
    assert response.status_code == 200
