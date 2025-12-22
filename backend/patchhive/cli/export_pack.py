from __future__ import annotations

import json
from pathlib import Path

from patchhive.export.export_pack import export_pack
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import CaseSpec, suggest_layouts
from patchhive.pipeline.run_library import run_library
from patchhive.schemas import RigSpec
from patchhive.schemas_library import PatchSpaceConstraints


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--rigspec", required=True)
    ap.add_argument("--gallery-root", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tier", default="core")
    ap.add_argument("--max-cables", type=int, default=6)
    ap.add_argument("--allow-feedback", action="store_true")
    ap.add_argument("--rows", type=int, default=1)
    ap.add_argument("--row-hp", type=int, default=104)
    ap.add_argument("--no-diagrams", action="store_true")
    args = ap.parse_args()

    rig = RigSpec.model_validate(json.loads(Path(args.rigspec).read_text(encoding="utf-8")))
    gallery = ModuleGalleryStore(args.gallery_root)

    canon = build_canonical_rig(rig, gallery_store=gallery)
    metrics = map_metrics(canon)
    layouts = suggest_layouts(canon, metrics, case=CaseSpec(rows=args.rows, row_hp=args.row_hp))

    best_layout = sorted(
        layouts,
        key=lambda layout: (
            -layout.score_breakdown.learning_gradient,
            -layout.total_score,
            layout.layout_type.value,
        ),
    )[0]
    layout_by_patch: dict[str, object] = {}

    constraints = PatchSpaceConstraints(
        tier=args.tier,
        max_cables=args.max_cables,
        allow_feedback=bool(args.allow_feedback),
        require_output_path=True,
    )

    library = run_library(canon, constraints=constraints, include_diagrams=not args.no_diagrams)

    manifest = export_pack(
        canon,
        library,
        out_dir=args.out_dir,
        layout_by_patch=layout_by_patch or {p.card.patch_id: best_layout for p in library.patches},
    )

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
