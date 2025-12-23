"""Resolve detected modules to gallery references."""

from __future__ import annotations

from patchhive.gallery.match import match_module
from patchhive.schemas import (
    CONFIRM_THRESHOLD,
    DetectedModule,
    Provenance,
    ProvenanceStatus,
    ProvenanceType,
    ResolvedModuleRef,
)


def resolve_modules_v1(
    detections: list[DetectedModule],
    gallery_entries: list,
) -> list[ResolvedModuleRef]:
    resolved: list[ResolvedModuleRef] = []
    for detection in detections:
        name_value = detection.name.value or ""
        manufacturer_value = detection.manufacturer.value if detection.manufacturer else None
        candidates = match_module(name_value, manufacturer_value, gallery_entries)
        if candidates:
            match_entry, score = candidates[0]
            status = (
                ProvenanceStatus.CONFIRMED
                if score >= CONFIRM_THRESHOLD
                else ProvenanceStatus.DISPUTED
            )
            resolved.append(
                ResolvedModuleRef(
                    detection_id=detection.detection_id,
                    gallery_entry_id=match_entry.entry_id,
                    match_confidence=score,
                    status=status,
                    module_spec=match_entry.spec,
                    provenance=Provenance(type=ProvenanceType.GALLERY),
                )
            )
        else:
            resolved.append(
                ResolvedModuleRef(
                    detection_id=detection.detection_id,
                    gallery_entry_id=None,
                    match_confidence=0.0,
                    status=ProvenanceStatus.MISSING,
                    module_spec=None,
                    provenance=Provenance(type=ProvenanceType.GALLERY),
                )
            )
    return resolved
