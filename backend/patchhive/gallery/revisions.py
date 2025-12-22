from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


@dataclass
class GalleryRevision:
    module_key: str
    payload: Dict[str, Any]
    revision_id: str = ""
    version: int = 0


def _canonical_hash(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def append_revision(gallery_root: str, revision: GalleryRevision, evidence_ref: str) -> GalleryRevision:
    """
    Append a gallery revision without overwriting previous versions.

    A new revision file is written under:
      {gallery_root}/modules/{module_key}/revisions/{revision_id}.json
    """
    root = Path(gallery_root)
    module_dir = root / "modules" / revision.module_key
    revisions_dir = module_dir / "revisions"
    revisions_dir.mkdir(parents=True, exist_ok=True)

    meta_path = module_dir / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        latest_version = int(meta.get("latest_version", -1))
    else:
        latest_version = -1

    revision.version = latest_version + 1
    revision.revision_id = f"rev.{_canonical_hash(revision.payload)}"

    rev_path = revisions_dir / f"{revision.revision_id}.json"
    if rev_path.exists():
        raise RuntimeError(f"Revision already exists for {revision.module_key}: {revision.revision_id}")

    record = {
        "module_key": revision.module_key,
        "revision_id": revision.revision_id,
        "version": revision.version,
        "payload": revision.payload,
        "meta": {
            "evidence_ref": evidence_ref,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
    }
    rev_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    meta = {
        "module_key": revision.module_key,
        "latest_revision_id": revision.revision_id,
        "latest_version": revision.version,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_ref": evidence_ref,
    }
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")

    return revision
