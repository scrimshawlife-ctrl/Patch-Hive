from __future__ import annotations

from fastapi.testclient import TestClient
from patchhive.api.app import app


def test_api_routes_exist():
    client = TestClient(app)
    r = client.get("/v1/runs/doesnotexist/summary")
    assert r.status_code in (404, 422)


def test_api_openapi_docs():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "openapi" in r.json()


def test_api_manifest_404():
    client = TestClient(app)
    r = client.get("/v1/runs/nonexistent/manifest")
    assert r.status_code == 404


def test_api_pdf_404():
    client = TestClient(app)
    r = client.get("/v1/runs/nonexistent/download/pdf")
    assert r.status_code == 404


def test_api_v2_job_404():
    client = TestClient(app)
    r = client.get("/v2/runs/nonexistent/job")
    assert r.status_code == 404


def test_api_v2_bundle_404():
    client = TestClient(app)
    r = client.get("/v2/runs/nonexistent/download/bundle.zip")
    assert r.status_code == 404


def test_api_v2_endpoints_in_openapi():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "v2/runs" in r.text or "/v2/" in r.text
