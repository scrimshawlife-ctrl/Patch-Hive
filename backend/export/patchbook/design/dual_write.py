"""Path A producer: dual-write sealed GeneratedPatchRecord rows at generate time."""

from __future__ import annotations

from sqlalchemy.orm import Session

from canon.models import GeneratedPatchRecord, PatchLibraryRecord, RigRevisionRecord
from export.patchbook.design.content_spine import (
    library_content_hash,
    seal_orm_patch_to_compilation,
    LoadedLibraryItem,
)
from patches.models import Patch
from runs.bridge import LegacyRunExportBridge


def dual_write_generated_patches(
    session: Session,
    *,
    bridge: LegacyRunExportBridge,
    patches: list[Patch],
) -> str | None:
    """Seal ORM patches into GeneratedPatchRecord ordered by list position.

    Idempotent for empty library: skips if rows already exist for the library.
    Returns library_content_hash or None if bridge not ready / no patches.
    """
    if not bridge.export_bridge_ready or not patches:
        return None

    library_id = f"library-{bridge.source_run_id}"
    library = session.get(PatchLibraryRecord, library_id)
    if library is None:
        return None

    existing = (
        session.query(GeneratedPatchRecord)
        .filter(GeneratedPatchRecord.patch_library_id == library_id)
        .count()
    )
    if existing > 0:
        # Already sealed — recompute hash from existing for return value
        rows = (
            session.query(GeneratedPatchRecord)
            .filter(GeneratedPatchRecord.patch_library_id == library_id)
            .order_by(GeneratedPatchRecord.position.asc())
            .all()
        )
        return _hash_from_generated_rows(rows)

    revision = session.get(RigRevisionRecord, bridge.rig_revision_id)
    snapshot = (
        revision.canonical_rig if revision and isinstance(revision.canonical_rig, dict) else {}
    )

    items: list[LoadedLibraryItem] = []
    for position, patch in enumerate(patches):
        compilation = seal_orm_patch_to_compilation(
            patch,
            source_run_id=bridge.source_run_id,
            source_rig_revision_id=bridge.rig_revision_id,
            rig_snapshot=snapshot,
            position=position,
        )
        row_id = f"gen-patch-{bridge.source_run_id}-{position}"
        session.add(
            GeneratedPatchRecord(
                id=row_id,
                patch_library_id=library_id,
                position=position,
                name=str(patch.name or f"Patch {position}"),
                patch_graph=compilation.patch_graph.canonical_dict(),
                patch_plan=compilation.patch_plan.canonical_dict(),
                validation_report=compilation.validation_report.canonical_dict(),
                variations=[],
                canonical_hash=compilation.canonical_hash_value(),
            )
        )
        items.append(
            LoadedLibraryItem(
                position=position,
                compilation=compilation,
                orm_patch_id=int(patch.id) if patch.id is not None else None,
                generated_patch_id=row_id,
            )
        )

    content_hash = library_content_hash(items)
    # PatchLibraryRecord is append-only — do not mutate library.canonical_hash.
    # Integrity lives on GeneratedPatchRecord.canonical_hash + library_content_hash
    # returned to callers / export seal (KD-19).
    session.flush()
    return content_hash


def _hash_from_generated_rows(rows: list[GeneratedPatchRecord]) -> str:
    from canon.contracts import canonical_sha256

    payload = [{"position": int(r.position), "canonical_hash": str(r.canonical_hash)} for r in rows]
    return canonical_sha256(payload)
