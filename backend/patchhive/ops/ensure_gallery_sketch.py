"""Ensure gallery entries have deterministic sketches."""
from __future__ import annotations

from patchhive.gallery.render_sketch import render_module_sketch_svg
from patchhive.schemas import ModuleGalleryEntry


def ensure_sketch(entry: ModuleGalleryEntry) -> ModuleGalleryEntry:
    if entry.sketch_svg:
        return entry
    updated = entry.model_copy(update={"sketch_svg": render_module_sketch_svg(entry)})
    return updated
