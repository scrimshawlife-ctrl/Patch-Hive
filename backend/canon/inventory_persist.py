"""Persist SystemInventoryRevision contracts to append-only ORM rows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from canon.models import SystemInventoryRevisionRecord
from canon.visual_contracts import SystemInventoryRevision


def persist_system_inventory_revision(
    db: Session,
    revision: SystemInventoryRevision,
    *,
    rack_id: int | None = None,
) -> SystemInventoryRevisionRecord:
    """Insert inventory revision if absent. Never mutates existing rows."""

    existing = db.get(SystemInventoryRevisionRecord, revision.inventory_revision_id)
    if existing is not None:
        return existing

    record = SystemInventoryRevisionRecord(
        id=revision.inventory_revision_id,
        system_id=revision.system_id,
        rack_id=rack_id,
        previous_revision_id=revision.previous_revision_id,
        schema_version="patchhive.inventory.v1",
        items=[item.model_dump(mode="json") for item in revision.items],
        unresolved_candidate_ids=list(revision.unresolved_candidate_ids),
        canonical_hash=revision.canonical_hash or revision.computed_hash(),
        created_by=revision.created_by,
        created_at=revision.created_at,
    )
    db.add(record)
    db.flush()
    return record


def load_system_inventory_revision(
    db: Session, inventory_revision_id: str
) -> SystemInventoryRevision | None:
    record = db.get(SystemInventoryRevisionRecord, inventory_revision_id)
    if record is None:
        return None
    return SystemInventoryRevision.model_validate(
        {
            "inventory_revision_id": record.id,
            "system_id": record.system_id,
            "previous_revision_id": record.previous_revision_id,
            "items": record.items or [],
            "unresolved_candidate_ids": record.unresolved_candidate_ids or [],
            "created_at": record.created_at,
            "created_by": record.created_by,
            "canonical_hash": record.canonical_hash,
        }
    )
