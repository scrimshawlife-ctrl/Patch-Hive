from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from patchhive.gallery.schemas_gallery_v2 import (
    ModuleGalleryRevision,
    FieldStatus,
    ProvenanceType,
)


def _meta(
    method: str,
    evidence_ref: str,
    provenance: ProvenanceType,
    status: FieldStatus,
    **extra: Any,
) -> Dict[str, Any]:
    """Create standardized metadata dict."""
    return {
        "method": method,
        "evidence_ref": evidence_ref,
        "provenance": provenance.value,
        "status": status.value,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **extra,
    }


def _revision_hash(rev: ModuleGalleryRevision) -> str:
    """Compute content-addressable revision ID."""
    # Serialize to canonical JSON
    data = rev.model_dump(mode="json", exclude={"revision_id", "version"})
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"rev.{h[:16]}"


class ModuleGalleryStoreV2:
    """
    Gallery store with revision control and filesystem persistence.

    Directory structure:
        {gallery_root}/
            modules/
                {module_key}/
                    revisions/
                        {revision_id}.json
                    assets/
                        {filename}
                    _meta.json  # Latest version pointer
    """

    def __init__(self, gallery_root: str):
        self.root = Path(gallery_root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.modules_dir = self.root / "modules"
        self.modules_dir.mkdir(exist_ok=True)

    def _module_dir(self, module_key: str) -> Path:
        """Get module directory."""
        return self.modules_dir / module_key

    def _revisions_dir(self, module_key: str) -> Path:
        """Get revisions directory for a module."""
        d = self._module_dir(module_key) / "revisions"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _assets_dir(self, module_key: str) -> Path:
        """Get assets directory for a module."""
        d = self._module_dir(module_key) / "assets"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _meta_path(self, module_key: str) -> Path:
        """Get meta file path for a module."""
        return self._module_dir(module_key) / "_meta.json"

    def read_latest(self, module_key: str) -> Optional[ModuleGalleryRevision]:
        """Read the latest revision for a module."""
        meta_path = self._meta_path(module_key)
        if not meta_path.exists():
            return None

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        latest_rev_id = meta.get("latest_revision_id")
        if not latest_rev_id:
            return None

        rev_path = self._revisions_dir(module_key) / f"{latest_rev_id}.json"
        if not rev_path.exists():
            return None

        return ModuleGalleryRevision.model_validate_json(rev_path.read_text(encoding="utf-8"))

    def read_all_revisions(self, module_key: str) -> List[ModuleGalleryRevision]:
        """Read all revisions for a module, sorted by version."""
        revs_dir = self._revisions_dir(module_key)
        if not revs_dir.exists():
            return []

        revisions = []
        for rev_file in revs_dir.glob("*.json"):
            rev = ModuleGalleryRevision.model_validate_json(rev_file.read_text(encoding="utf-8"))
            revisions.append(rev)

        return sorted(revisions, key=lambda r: r.version)

    def append_revision(
        self,
        revision: ModuleGalleryRevision,
        evidence_ref: str,
    ) -> ModuleGalleryRevision:
        """
        Append a new revision to the module.

        If this is the first revision, version=0.
        Otherwise, version = latest.version + 1.
        """
        module_key = revision.module_key

        # Get current latest
        latest = self.read_latest(module_key)
        if latest is None:
            version = 0
        else:
            version = latest.version + 1

        # Update version
        revision.version = version

        # Compute revision ID
        revision.revision_id = _revision_hash(revision)

        # Write revision file
        rev_path = self._revisions_dir(module_key) / f"{revision.revision_id}.json"
        rev_path.write_text(revision.model_dump_json(indent=2), encoding="utf-8")

        # Update meta
        meta = {
            "module_key": module_key,
            "latest_revision_id": revision.revision_id,
            "latest_version": version,
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "evidence_ref": evidence_ref,
        }
        self._meta_path(module_key).write_text(
            json.dumps(meta, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return revision

    def write_asset(self, module_key: str, filename: str, data: bytes) -> str:
        """
        Write an asset file for a module.

        Returns the relative path to the asset (for use in attachment refs).
        """
        asset_path = self._assets_dir(module_key) / filename
        asset_path.write_bytes(data)
        # Return path relative to gallery root
        return str(asset_path.relative_to(self.root))
