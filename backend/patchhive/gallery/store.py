from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

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
    Append-only revisions for ModuleGalleryEntry.
    """

    def __init__(self, root: str | Path) -> None:
        self.paths = GalleryPaths(root=Path(root))
        self.paths.root.mkdir(parents=True, exist_ok=True)

    def list_revisions(self, module_gallery_id: str) -> List[Path]:
        d = self.paths.module_dir(module_gallery_id)
        if not d.exists():
            return []
        return sorted([p for p in d.iterdir() if p.suffix == ".json"])

    def get_latest(self, module_gallery_id: str) -> Optional[ModuleGalleryEntry]:
        revs = self.list_revisions(module_gallery_id)
        if not revs:
            return None
        raw = json.loads(revs[-1].read_text(encoding="utf-8"))
        return ModuleGalleryEntry.model_validate(raw)

    def append_revision(self, entry: ModuleGalleryEntry) -> Path:
        path = self.paths.rev_path(entry.module_gallery_id, entry.rev)
        if path.exists():
            raise ValueError("Gallery rev collision. Provide unique rev timestamp.")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(entry.to_canonical_dict(), sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        tmp.replace(path)
        return path
