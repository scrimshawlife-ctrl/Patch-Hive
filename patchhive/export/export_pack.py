from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from patchhive.schemas import CanonicalRig
from patchhive.schemas_library import PatchLibrary


def export_pack(canon: CanonicalRig, library: PatchLibrary, *, out_dir: str) -> Dict[str, str]:
    out_path = Path(out_dir)
    json_dir = out_path / "json"
    pdf_dir = out_path / "pdf"
    json_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    library_json = json_dir / "library.json"
    payload = {
        "rig_id": canon.rig_id,
        "library": library.to_dict(),
    }
    library_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    manifest = {
        "rig_id": canon.rig_id,
        "library_json": str(library_json),
        "pdf_dir": str(pdf_dir),
    }
    (json_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
