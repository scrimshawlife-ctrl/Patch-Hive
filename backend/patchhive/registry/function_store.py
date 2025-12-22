from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from patchhive.schemas import JackFunctionEntry


@dataclass(frozen=True)
class RegistryPaths:
    root: Path

    def fn_dir(self, function_id: str) -> Path:
        safe = function_id.replace("/", "_")
        return self.root / safe

    def rev_path(self, function_id: str, rev: datetime) -> Path:
        iso = rev.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        return self.fn_dir(function_id) / f"{iso}.json"


class JackFunctionStore:
    """
    Append-only revisions for JackFunctionEntry.
    Mirrors ModuleGalleryStore semantics.
    """

    def __init__(self, root: str | Path) -> None:
        self.paths = RegistryPaths(root=Path(root))
        self.paths.root.mkdir(parents=True, exist_ok=True)

    def list_revisions(self, function_id: str) -> List[Path]:
        d = self.paths.fn_dir(function_id)
        if not d.exists():
            return []
        return sorted([p for p in d.iterdir() if p.suffix == ".json"])

    def get_latest(self, function_id: str) -> Optional[JackFunctionEntry]:
        revs = self.list_revisions(function_id)
        if not revs:
            return None
        raw = json.loads(revs[-1].read_text(encoding="utf-8"))
        return JackFunctionEntry.model_validate(raw)

    def append_revision(self, entry: JackFunctionEntry) -> Path:
        path = self.paths.rev_path(entry.function_id, entry.rev)
        if path.exists():
            raise ValueError("Function rev collision. Provide unique rev timestamp.")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(entry.to_canonical_dict(), sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        tmp.replace(path)
        return path
