from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from patchhive.export.export_library_pdf import export_library_pdf
from patchhive.render.diagram_scene import build_scene
from patchhive.render.diagram_svg import scene_to_svg
from patchhive.schemas import CanonicalRig, SuggestedLayout
from patchhive.schemas_library import PatchLibrary


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return _sha256_bytes(text.encode("utf-8"))


def _write_json(path: Path, obj: object) -> str:
    if isinstance(obj, str):
        payload = obj
    else:
        payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _write_text(path, payload)


def export_pack(
    canon: CanonicalRig,
    library: PatchLibrary,
    *,
    out_dir: str,
    layout_by_patch: Optional[dict[str, SuggestedLayout]] = None,
) -> Dict[str, object]:
    """
    Writes a deterministic export pack.
    """
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, object] = {
        "generated_at": _now_utc().isoformat(),
        "rig_id": canon.rig_id,
        "patch_count": len(library.patches),
        "paths": {},
        "hashes": {},
        "stats": {
            "categories": {},
            "difficulty": {},
        },
    }

    lib_json = library.model_dump(mode="json")
    h_lib = _write_json(root / "library.json", lib_json)
    manifest["paths"]["library"] = "library.json"
    manifest["hashes"]["library.json"] = h_lib

    cat_counts: Dict[str, int] = {}
    diff_counts: Dict[str, int] = {}
    (root / "svgs").mkdir(parents=True, exist_ok=True)

    for item in library.patches:
        cat_counts[item.card.category.value] = cat_counts.get(item.card.category.value, 0) + 1
        diff_counts[item.card.difficulty.value] = diff_counts.get(item.card.difficulty.value, 0) + 1

        layout = layout_by_patch.get(item.card.patch_id) if layout_by_patch else None
        scene = build_scene(canon, item.patch, layout=layout)
        svg = scene_to_svg(scene)

        rel = f"svgs/{item.card.patch_id}.svg"
        h_svg = _write_text(root / rel, svg)
        manifest["paths"].setdefault("svgs", []).append(rel)
        manifest["hashes"][rel] = h_svg

    manifest["stats"]["categories"] = dict(sorted(cat_counts.items()))
    manifest["stats"]["difficulty"] = dict(sorted(diff_counts.items()))

    pdf_rel = "pdf/patchbook.pdf"
    pdf_abs = str(root / pdf_rel)
    export_library_pdf(canon, library, out_pdf=pdf_abs, layout_by_patch=layout_by_patch)

    pdf_bytes = (root / pdf_rel).read_bytes()
    manifest["paths"]["pdf"] = pdf_rel
    manifest["hashes"][pdf_rel] = _sha256_bytes(pdf_bytes)

    h_manifest = _write_json(root / "manifest.json", manifest)
    manifest["hashes"]["manifest.json"] = h_manifest

    return manifest
