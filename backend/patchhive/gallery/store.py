from __future__ import annotations

from typing import Dict, List, Optional


class ModuleGalleryStore:
    """
    Minimal in-memory gallery store with revision awareness.

    This store is append-only and designed for deterministic test flows.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._entries: Dict[str, List[object]] = {}

    def append_revision(self, entry: object) -> None:
        module_id = getattr(entry, "module_gallery_id", None)
        if module_id is None:
            raise ValueError("Gallery entry missing module_gallery_id")
        self._entries.setdefault(module_id, []).append(entry)

    def get_latest(self, module_id: str) -> Optional[object]:
        revs = self._entries.get(module_id, [])
        return revs[-1] if revs else None

    def list_revisions(self, module_id: str) -> List[object]:
        return list(self._entries.get(module_id, []))

    def load_revision(self, module_id: str, revision_ref: object) -> object:
        if revision_ref in self._entries.get(module_id, []):
            return revision_ref
        raise KeyError(f"Revision not found for module: {module_id}")
