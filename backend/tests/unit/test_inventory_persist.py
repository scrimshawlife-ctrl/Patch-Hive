"""Persist SystemInventoryRevision via Alembic-backed ORM models."""

from sqlalchemy.orm import Session

from canon.inventory_persist import (
    load_system_inventory_revision,
    persist_system_inventory_revision,
)
from canon.models import SystemInventoryRevisionRecord
from patches.engine import generate_patches_with_ir
from patches.inventory_gate import build_manual_inventory_from_rack
from racks.models import Rack


def test_persist_and_load_inventory_revision(db_session: Session, sample_rack_basic: Rack) -> None:
    revision = build_manual_inventory_from_rack(db_session, sample_rack_basic)
    record = persist_system_inventory_revision(db_session, revision, rack_id=sample_rack_basic.id)
    db_session.commit()
    assert record.id == revision.inventory_revision_id
    loaded = load_system_inventory_revision(db_session, revision.inventory_revision_id)
    assert loaded is not None
    assert loaded.canonical_hash == revision.canonical_hash
    assert len(loaded.items) == len(revision.items)

    # Idempotent second persist
    again = persist_system_inventory_revision(db_session, revision, rack_id=sample_rack_basic.id)
    assert again.id == record.id
    assert db_session.query(SystemInventoryRevisionRecord).count() == 1


def test_generate_persists_inventory_revision(db_session: Session, sample_rack_basic: Rack) -> None:
    _ir, _graphs, provenance = generate_patches_with_ir(db_session, sample_rack_basic, seed=7)
    db_session.commit()
    metrics = provenance.to_dict()["metrics"]
    inv_id = (
        metrics.get("inventory_revision_id") or metrics["inventory_gate"]["inventory_revision_id"]
    )
    assert db_session.get(SystemInventoryRevisionRecord, inv_id) is not None
