"""Append-only Module Gallery revision store."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from patchhive.schemas import ModuleGalleryEntry


@dataclass(frozen=True)
class GalleryPaths:
    root: Path

    def module_dir(self, module_gallery_id: str) -> Path:
        safe = module_gallery_id.replace("/", "_")
        return self.root / safe

    def rev_path(self, module_gallery_id: str, rev: datetime) -> Path:
        iso = rev.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        return self.module_dir(module_gallery_id) / f"{iso}.json"


class ModuleGalleryStore:
    """
    Append-only revision store.

    Storage layout:
      <root>/
        mod.make_noise.maths/
          20251221T235800.000000Z.json
          20251222T010203.123456Z.json
    """

    def __init__(self, root: str | Path) -> None:
        self.paths = GalleryPaths(root=Path(root))
        self.paths.root.mkdir(parents=True, exist_ok=True)

    def _write_json_atomic(self, path: Path, data: Dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        tmp.replace(path)

    def _read_entry(self, path: Path) -> ModuleGalleryEntry:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return ModuleGalleryEntry.model_validate(raw)

    def list_revisions(self, module_gallery_id: str) -> List[Path]:
        directory = self.paths.module_dir(module_gallery_id)
        if not directory.exists():
            return []
        return sorted([path for path in directory.iterdir() if path.suffix == ".json"])

    def list_module_ids(self) -> List[str]:
        if not self.paths.root.exists():
            return []
        return sorted([path.name for path in self.paths.root.iterdir() if path.is_dir()])

    def load_revision(self, module_gallery_id: str, rev_path: Path) -> ModuleGalleryEntry:
        module_dir = self.paths.module_dir(module_gallery_id).resolve()
        resolved = rev_path.resolve()
        if module_dir not in resolved.parents:
            raise ValueError("rev_path is not inside module directory")
        return self._read_entry(resolved)

    def get_latest(self, module_gallery_id: str) -> Optional[ModuleGalleryEntry]:
        revs = self.list_revisions(module_gallery_id)
        if not revs:
            return None
        return self._read_entry(revs[-1])

    def list_latest_entries(self) -> List[ModuleGalleryEntry]:
        entries: List[ModuleGalleryEntry] = []
        for module_id in self.list_module_ids():
            entry = self.get_latest(module_id)
            if entry is not None:
                entries.append(entry)
        return entries

    def append_revision(self, entry: ModuleGalleryEntry) -> Path:
        path = self.paths.rev_path(entry.module_gallery_id, entry.rev)
        if path.exists():
            raise ValueError("Revision already exists (rev collision). Provide a unique rev timestamp.")
        self._write_json_atomic(path, entry.to_canonical_dict())
        return path

    def ensure_appended_if_changed(
        self,
        new_entry: ModuleGalleryEntry,
        *,
        compare_to_latest: bool = True,
    ) -> Tuple[bool, Optional[Path]]:
        if not compare_to_latest:
            return True, self.append_revision(new_entry)

        latest = self.get_latest(new_entry.module_gallery_id)
        if latest is None:
            return True, self.append_revision(new_entry)

        new_dict = new_entry.to_canonical_dict()
        old_dict = latest.to_canonical_dict()
        new_dict.pop("rev", None)
        old_dict.pop("rev", None)

        if new_dict == old_dict:
            return False, None

        return True, self.append_revision(new_entry)


def get_default_store() -> ModuleGalleryStore:
    return ModuleGalleryStore(Path(__file__).resolve().parent / "data")
