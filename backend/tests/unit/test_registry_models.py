"""Basic unit tests for Device Registry models and services."""

from registry.models import Manufacturer, DeviceModel
from registry.services import list_manufacturers, search_models, get_coverage_report


def test_registry_models_import():
    """Models should be importable and have expected attributes."""
    assert hasattr(Manufacturer, "__table__")
    assert hasattr(DeviceModel, "hp")
    assert "slug" in [c.name for c in Manufacturer.__table__.columns]


def test_services_snapshot_based(monkeypatch):
    """Services should work against the generated latest snapshot."""
    # The ingestion script produces registry_latest.json
    mans = list_manufacturers(limit=5)
    assert isinstance(mans, list)
    if mans:
        assert "name" in mans[0] or "canonical_name" in mans[0]

    results = search_models(q="math", limit=3)
    assert isinstance(results, list)

    cov = get_coverage_report()
    assert "total_manufacturers" in cov or "total_models" in cov
