"""Test that materialization wires registry slugs from catalog."""

import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_materialize_carries_registry_links():
    """Materialize a catalog entry that has registry links and verify they are copied."""
    # Find a seeded catalog entry with both HP and registry link
    cat_resp = client.get("/api/modules/catalog?limit=50")
    assert cat_resp.status_code == 200
    entries = cat_resp.json().get("modules", [])
    
    candidate = None
    for e in entries:
        if e.get("hp") is not None and e.get("registry_manufacturer_slug"):
            candidate = e
            break
    
    assert candidate is not None, "No suitable catalog entry with hp + registry link found"
    
    slug = candidate["slug"]
    mat = client.post(f"/api/modules/catalog/{slug}/materialize")
    assert mat.status_code in (200, 201)
    
    data = mat.json()
    assert "module" in data
    mod = data["module"]
    
    assert mod.get("registry_manufacturer_slug") == candidate.get("registry_manufacturer_slug")
    # device slug may be None for some
    if candidate.get("registry_device_slug"):
        assert mod.get("registry_device_slug") == candidate.get("registry_device_slug")
