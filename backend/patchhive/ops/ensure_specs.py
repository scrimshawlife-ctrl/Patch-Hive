"""Ensure module specs are available or explicitly missing."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from core.discovery import register_function
from patchhive.ops.ensure_gallery_sketch import ensure_sketch
from patchhive.schemas import ModuleGalleryEntry, ProvenanceRecord, ResolvedModuleRef, RigSourceType
from patchhive.gallery.store import ModuleGalleryStore


def _make_stub_entry(
    module_id: str,
    label: str,
    manufacturer: str,
    timestamp: datetime,
    evidence_ref: str,
    provenance_type: str,
) -> ModuleGalleryEntry:
    return ModuleGalleryEntry(
        module_gallery_id=module_id,
        rev=timestamp,
        name=label,
        manufacturer=manufacturer,
        hp=0,
        power=None,
        jacks=[],
        modes=None,
        provenance=[
            ProvenanceRecord(
                type=provenance_type,
                model_version=None,
                timestamp=timestamp,
                evidence_ref=evidence_ref,
            )
        ],
        notes=["temporary stub", "specs missing"],
    )


def ensure_module_specs(
    resolved_modules: List[ResolvedModuleRef],
    store: ModuleGalleryStore,
    rig_source: RigSourceType,
    timestamp: Optional[datetime] = None,
    allow_vision_writeback: bool = False,
) -> List[ModuleGalleryEntry]:
    now = timestamp or datetime.utcnow()
    entries: List[ModuleGalleryEntry] = []
    for resolved in sorted(resolved_modules, key=lambda r: r.detected_id):
        if resolved.gallery_module_id:
            entry = store.get_latest(resolved.gallery_module_id)
            if entry is None:
                continue
            if rig_source in {"manual_picklist", "hybrid"} or allow_vision_writeback:
                updated = entry.model_copy(
                    update={
                        "provenance": [
                            *entry.provenance,
                            ProvenanceRecord(
                                type="manual" if rig_source != "photo_gemini" else "gemini",
                                model_version=None,
                                timestamp=now,
                                evidence_ref=resolved.detected_id,
                            ),
                        ],
                    }
                )
                updated = ensure_sketch(updated)
                updated = updated.model_copy(update={"rev": now})
                store.ensure_appended_if_changed(updated)
                entries.append(updated)
            else:
                entries.append(entry)
        else:
            stub_id = resolved.unknown_stub_id or f"unknown:{resolved.detected_id}"
            provenance_type = "manual" if rig_source != "photo_gemini" else "derived"
            stub = _make_stub_entry(
                module_id=stub_id,
                label="Unknown Module",
                manufacturer="Unknown",
                timestamp=now,
                evidence_ref=resolved.detected_id,
                provenance_type=provenance_type,
            )
            if rig_source in {"manual_picklist", "hybrid"}:
                stub = ensure_sketch(stub)
                store.append_revision(stub)
            entries.append(stub)
    return entries


register_function(
    name="ensure_module_specs",
    function=ensure_module_specs,
    description="Ensure module specs are resolved or explicitly missing.",
    input_model="List[ResolvedModuleRef], ModuleGalleryStore, RigSourceType",
    output_model="List[ModuleGalleryEntry]",
)
