from __future__ import annotations

from patchhive.schemas import ModuleGalleryEntry


def ensure_sketch(entry: ModuleGalleryEntry) -> ModuleGalleryEntry:
    """
    Preserve existing sketch data on gallery revisions.
    """
    return entry
