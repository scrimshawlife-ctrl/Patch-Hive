"""Ensure module specs exist and append new gallery revisions if needed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from patchhive.schemas import (
    ModuleGalleryEntry,
    ModuleSpec,
    Provenance,
    ProvenanceType,
    ResolvedModuleRef,
)


@dataclass
class EnsuredSpecResult:
    resolved: list[ResolvedModuleRef]
    new_entries: list[ModuleGalleryEntry]


def ensure_module_specs_v1(
    resolved_refs: list[ResolvedModuleRef],
    gallery_entries: list[ModuleGalleryEntry],
    default_provenance: Optional[Provenance] = None,
) -> EnsuredSpecResult:
    """Create new gallery entries for missing specs.

    This does not invent missing power specs; unknown remains None.
    """
    provenance = default_provenance or Provenance(type=ProvenanceType.DERIVED)
    new_entries: list[ModuleGalleryEntry] = []
    updated_refs: list[ResolvedModuleRef] = []
    for ref in resolved_refs:
        if ref.module_spec is not None:
            updated_refs.append(ref)
            continue
        entry_id = ref.gallery_entry_id or f"unknown-{ref.detection_id}"
        existing_revisions = [entry for entry in gallery_entries if entry.entry_id == entry_id]
        revision_index = len(existing_revisions) + 1
        previous_revision_id = existing_revisions[-1].revision_id if existing_revisions else None
        module_spec = ModuleSpec(
            module_id=entry_id,
            name=entry_id,
            manufacturer=None,
            width_hp=None,
            sections=[],
            normalled_edges=[],
            power_12v_ma=None,
            power_minus12v_ma=None,
            power_5v_ma=None,
        )
        new_entry = ModuleGalleryEntry(
            entry_id=entry_id,
            revision_id=f"{entry_id}-rev{revision_index}",
            previous_revision_id=previous_revision_id,
            created_at=provenance.timestamp,
            name=module_spec.name,
            manufacturer=None,
            spec=module_spec,
            provenance=provenance,
        )
        new_entries.append(new_entry)
        updated_refs.append(
            ref.model_copy(update={"gallery_entry_id": entry_id, "module_spec": module_spec})
        )
    return EnsuredSpecResult(resolved=updated_refs, new_entries=new_entries)
