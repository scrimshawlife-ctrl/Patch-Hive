"""Append-only module gallery storage."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from patchhive.schemas import ModuleGalleryEntry


@dataclass
class GalleryRecord:
    entry: ModuleGalleryEntry


class ModuleGalleryStore:
    """Append-only storage for module gallery revisions."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def append(self, entry: ModuleGalleryEntry) -> None:
        record = entry.model_dump(mode="json")
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")

    def iter_entries(self) -> Iterable[ModuleGalleryEntry]:
        if not self.path.exists():
            return []
        entries: list[ModuleGalleryEntry] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            entries.append(ModuleGalleryEntry.model_validate(data))
        return entries

    def latest_revision(self, entry_id: str) -> Optional[ModuleGalleryEntry]:
        candidates = [entry for entry in self.iter_entries() if entry.entry_id == entry_id]
        if not candidates:
            return None
        candidates.sort(key=lambda item: item.created_at)
        return candidates[-1]

    def history(self, entry_id: str) -> list[ModuleGalleryEntry]:
        entries = [entry for entry in self.iter_entries() if entry.entry_id == entry_id]
        entries.sort(key=lambda item: item.created_at)
        return entries
