from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from patchhive.schemas import (
    NormalledBehavior,
    NormalledEdge,
    RigModuleInstance,
    RigSource,
    RigSpec,
)
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import suggest_layouts, CaseSpec
from patchhive.pipeline.run_library import run_library
from patchhive.presets.library_presets import starter_preset, core_preset, deep_preset
from patchhive.ops.prune_library import prune_library, LibraryPruneSpec
from patchhive.export.export_pack import export_pack
from patchhive.export.export_library_pdf_interactive import export_library_pdf_interactive


def _pick_constraints(name: str):
    n = (name or "core").lower()
    if n == "starter":
        return starter_preset()
    if n == "deep":
        return deep_preset()
    return core_preset()


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _rigspec_from_json(payload: Dict[str, Any]) -> RigSpec:
    modules = [
        RigModuleInstance(
            instance_id=mod["instance_id"],
            gallery_module_id=mod["gallery_module_id"],
            gallery_rev=_parse_datetime(mod.get("gallery_rev")),
            observed_placement=mod.get("observed_placement"),
            meta=None,
        )
        for mod in payload.get("modules", [])
    ]

    normalled_edges = [
        NormalledEdge(
            from_jack=edge["from_jack"],
            to_jack=edge["to_jack"],
            behavior=NormalledBehavior(edge.get("behavior", NormalledBehavior.break_on_insert.value)),
            meta=None,
        )
        for edge in payload.get("normalled_edges", [])
    ]

    return RigSpec(
        rig_id=payload["rig_id"],
        name=payload.get("name", payload["rig_id"]),
        source=RigSource(payload.get("source", RigSource.manual_picklist.value)),
        modules=modules,
        normalled_edges=normalled_edges,
        provenance=[],
        notes=list(payload.get("notes", [])),
    )


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--rigspec", required=True)
    ap.add_argument("--gallery-root", required=True)
    ap.add_argument("--out-dir", required=True)

    # presets
    ap.add_argument("--preset", default="core")  # starter|core|deep

    # pruning knobs (simple v1)
    ap.add_argument("--max-total", type=int, default=160)
    ap.add_argument("--max-per-category", type=int, default=70)
    ap.add_argument("--drop-runaway", action="store_true")
    ap.add_argument("--drop-silence", action="store_true")

    # weights: pass JSON dict strings
    ap.add_argument(
        "--category-weights",
        default=(
            '{"Voice":2.0,"Clock-Rhythm":1.4,"Generative":0.8,"Study":0.7,'
            '"Utility":0.6,"Texture-FX":1.0,"Performance Macro":1.0}'
        ),
    )
    ap.add_argument(
        "--difficulty-weights",
        default='{"Beginner":2.0,"Intermediate":1.2,"Advanced":0.9,"Experimental":0.5}',
    )

    # case
    ap.add_argument("--rows", type=int, default=1)
    ap.add_argument("--row-hp", type=int, default=104)

    args = ap.parse_args()

    rig_payload = json.loads(Path(args.rigspec).read_text(encoding="utf-8"))
    rig = _rigspec_from_json(rig_payload)
    gallery = ModuleGalleryStore(args.gallery_root)

    canon = build_canonical_rig(rig, gallery_store=gallery)

    constraints = _pick_constraints(args.preset)
    lib = run_library(canon, constraints=constraints, include_diagrams=False)

    prune_spec = LibraryPruneSpec(
        max_total=args.max_total,
        max_per_category=args.max_per_category,
        category_weights=json.loads(args.category_weights),
        difficulty_weights=json.loads(args.difficulty_weights),
        drop_runaway=bool(args.drop_runaway),
        drop_silence=bool(args.drop_silence),
    )
    lib2 = prune_library(lib, prune_spec)

    metrics = map_metrics(canon)
    layouts = suggest_layouts(canon, metrics, case=CaseSpec(rows=args.rows, row_hp=args.row_hp))
    layout_by_patch = {p.patch.patch_id: layouts[0] for p in lib2.patches} if layouts else {}

    # export pack (JSON + SVGs + basic PDF)
    manifest = export_pack(canon, lib2, out_dir=args.out_dir)

    # overwrite PDF with interactive version
    pdf_path = str(Path(args.out_dir) / "pdf" / "patchbook.pdf")
    export_library_pdf_interactive(canon, lib2, out_pdf=pdf_path, layout_by_patch=layout_by_patch)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
