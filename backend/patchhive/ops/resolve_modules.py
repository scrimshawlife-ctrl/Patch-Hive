"""Resolve detections against Module Gallery."""
from __future__ import annotations

import hashlib
from typing import List

from core.discovery import register_function
from patchhive.schemas import DetectedModule, ResolvedModuleRef
from patchhive.gallery.match import exact_match, fuzzy_match
from patchhive.gallery.store import ModuleGalleryStore


def _stub_id(label: str) -> str:
    return f"unknown:{hashlib.sha256(label.encode()).hexdigest()[:12]}"


def resolve_modules(
    detected_modules: List[DetectedModule],
    store: ModuleGalleryStore,
) -> List[ResolvedModuleRef]:
    gallery_entries = store.list_latest_entries()
    resolved: List[ResolvedModuleRef] = []
    for detected in sorted(detected_modules, key=lambda d: d.temp_id):
        exact = exact_match(
            gallery_entries,
            manufacturer=detected.brand_guess,
            name=detected.label_guess,
        )
        if exact:
            resolved.append(
                ResolvedModuleRef(
                    detected_id=detected.temp_id,
                    gallery_module_id=exact.module_gallery_id,
                    match_method="exact",
                    confidence=min(1.0, detected.confidence + 0.15),
                    status="inferred",
                )
            )
            continue
        fuzzy = fuzzy_match(
            gallery_entries,
            manufacturer=detected.brand_guess,
            name=detected.label_guess,
            hp_guess=detected.hp_guess,
        )
        if fuzzy:
            resolved.append(
                ResolvedModuleRef(
                    detected_id=detected.temp_id,
                    gallery_module_id=fuzzy.module_gallery_id,
                    match_method="fuzzy",
                    confidence=min(1.0, detected.confidence * fuzzy.score),
                    status="inferred",
                )
            )
            continue
        resolved.append(
            ResolvedModuleRef(
                detected_id=detected.temp_id,
                unknown_stub_id=_stub_id(detected.label_guess),
                match_method="stub",
                confidence=detected.confidence,
                status="missing",
            )
        )
    return resolved


register_function(
    name="resolve_modules",
    function=resolve_modules,
    description="Resolve detected modules against the Module Gallery.",
    input_model="List[DetectedModule], ModuleGalleryStore",
    output_model="List[ResolvedModuleRef]",
)
