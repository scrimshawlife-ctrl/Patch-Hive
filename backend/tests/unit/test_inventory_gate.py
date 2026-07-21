"""Confirmed-inventory gate for rack-backed patch generation."""

from sqlalchemy.orm import Session

from patches.engine import generate_patches_with_ir
from patches.inventory_gate import (
    build_manual_inventory_from_rack,
    evaluate_rack_inventory_gate,
    filter_patches_to_confirmed_modules,
)
from racks.models import Rack


def test_manual_inventory_from_rack_marks_modules_confirmed(
    db_session: Session, sample_rack_basic: Rack
) -> None:
    inventory = build_manual_inventory_from_rack(db_session, sample_rack_basic)
    assert inventory.canonical_hash == inventory.computed_hash()
    assert inventory.items
    assert all(item.resolution.value == "USER_CONFIRMED" for item in inventory.items)
    assert inventory.system_id == f"rack-{sample_rack_basic.id}"


def test_empty_rack_inventory_not_computable(db_session: Session, sample_rack_empty: Rack) -> None:
    report, patches = evaluate_rack_inventory_gate(db_session, sample_rack_empty)
    assert report.ready is False
    assert report.code == "NOT_COMPUTABLE"
    assert patches == []


def test_filter_drops_foreign_module_connections(
    db_session: Session, sample_rack_basic: Rack
) -> None:
    report, _ = evaluate_rack_inventory_gate(db_session, sample_rack_basic)
    allowed = report.allowed_catalog_module_ids
    assert allowed
    known = next(iter(allowed))
    foreign_id = max(allowed) + 9999

    class _Conn:
        def __init__(self, from_module_id: int, to_module_id: int) -> None:
            self.from_module_id = from_module_id
            self.to_module_id = to_module_id

    class _Patch:
        def __init__(self, connections: list[_Conn]) -> None:
            self.connections = connections
            self.name = "x"

    good = _Patch([_Conn(known, known)])
    bad = _Patch([_Conn(known, foreign_id)])
    kept, dropped, messages = filter_patches_to_confirmed_modules([good, bad], allowed)
    assert dropped == 1
    assert len(kept) == 1
    assert messages


def test_generate_with_ir_records_inventory_gate(
    db_session: Session, sample_rack_basic: Rack
) -> None:
    _ir, graphs, provenance = generate_patches_with_ir(db_session, sample_rack_basic, seed=42)
    metrics = provenance.to_dict()["metrics"]
    assert "inventory_gate" in metrics
    assert metrics["inventory_gate"]["ready"] is True
    assert metrics.get("inventory_revision_id") or metrics["inventory_gate"].get(
        "inventory_revision_id"
    )
    assert metrics.get("generation_status") in {"OK", "FILTERED"}
    report, _ = evaluate_rack_inventory_gate(db_session, sample_rack_basic)
    for graph in graphs:
        for conn in graph.connections:
            assert conn.from_module_id in report.allowed_catalog_module_ids
            assert conn.to_module_id in report.allowed_catalog_module_ids


def test_generate_empty_rack_is_not_computable(
    db_session: Session, sample_rack_empty: Rack
) -> None:
    _ir, graphs, provenance = generate_patches_with_ir(db_session, sample_rack_empty, seed=42)
    assert graphs == []
    metrics = provenance.to_dict()["metrics"]
    assert metrics["generation_status"] == "NOT_COMPUTABLE"
    assert metrics["inventory_gate"]["code"] == "NOT_COMPUTABLE"
