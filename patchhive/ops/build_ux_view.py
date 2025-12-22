from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from patchhive.schemas_ux import PatchLibraryUX, PatchExportItem


def build_ux_view(*, run_root: str, run_id: str) -> PatchLibraryUX:
    """
    Build a UX-friendly view of the patch library from stored artifacts.
    """
    root = Path(run_root)

    lib_path = root / "json" / "library.json"
    man_path = root / "manifest.json"

    lib = json.loads(lib_path.read_text(encoding="utf-8"))
    man = json.loads(man_path.read_text(encoding="utf-8"))

    # compute counts from manifest.stats if available
    cats: Dict[str, int] = man.get("stats", {}).get("categories", {})
    diffs: Dict[str, int] = man.get("stats", {}).get("difficulty", {})

    # If stats not in manifest, compute from library items
    if not cats or not diffs:
        cats_computed: Dict[str, int] = {}
        diffs_computed: Dict[str, int] = {}
        for it in lib.get("patches", []):
            card = it.get("card", {})
            cat = card.get("category", "Unknown")
            diff = card.get("difficulty", "Unknown")
            cats_computed[cat] = cats_computed.get(cat, 0) + 1
            diffs_computed[diff] = diffs_computed.get(diff, 0) + 1
        if not cats:
            cats = cats_computed
        if not diffs:
            diffs = diffs_computed

    items = []
    for it in lib.get("patches", []):
        card = it.get("card", {})
        patch_id = card.get("patch_id", "unknown")
        items.append(PatchExportItem(
            patch_id=patch_id,
            name=card.get("name", "Unnamed"),
            category=card.get("category", "Unknown"),
            difficulty=card.get("difficulty", "Unknown"),
            cable_count=card.get("cable_count", 0),
            stability_score=card.get("stability_score", 0.0),
            warnings=card.get("warnings", []),
            tags=card.get("tags", []),
            svg_path=f"svgs/{patch_id}.svg",
        ))

    # stable sort: category -> difficulty -> name
    items.sort(key=lambda x: (x.category, x.difficulty, x.name, x.patch_id))

    return PatchLibraryUX(
        run_id=run_id,
        rig_id=man.get("rig_id", "unknown"),
        patch_count=len(items),
        categories=cats,
        difficulty=diffs,
        items=items,
        download_pdf_url=f"/v2/runs/{run_id}/download/pdf",
        download_bundle_url=f"/v2/runs/{run_id}/download/bundle.zip",
    )
