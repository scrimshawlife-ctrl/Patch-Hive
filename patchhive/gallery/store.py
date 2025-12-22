from __future__ import annotations

from typing import Dict

from patchhive.schemas import CanonicalJack, CanonicalMode, CanonicalModule, ModuleGalleryEntry


class ModuleGalleryStore:
    def __init__(self, path) -> None:
        self.path = path
        self._entries: Dict[str, ModuleGalleryEntry] = {}

    def append_revision(self, entry: ModuleGalleryEntry) -> None:
        self._entries[entry.module_gallery_id] = entry

    def get_module(self, module_id: str) -> ModuleGalleryEntry:
        return self._entries[module_id]

    def find_by_name(self, *, name: str, manufacturer: str | None = None) -> ModuleGalleryEntry | None:
        for entry in self._entries.values():
            if entry.name != name:
                continue
            if manufacturer and entry.manufacturer != manufacturer:
                continue
            return entry
        return None

    def to_canonical(self, module_id: str, instance_id: str) -> CanonicalModule:
        entry = self.get_module(module_id)
        return CanonicalModule(
            instance_id=instance_id,
            hp=entry.hp,
            tags=list(entry.tags),
            modes=[CanonicalMode(name=mode, tags=[]) for mode in entry.modes],
            jacks=[
                CanonicalJack(
                    jack_id=jack.jack_id,
                    label=jack.label,
                    dir=jack.dir,
                    signal=jack.signal,
                )
                for jack in entry.jacks
            ],
        )
