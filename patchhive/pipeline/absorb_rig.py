from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from patchhive.schemas_rigspec_v2 import RigSpecV2
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.gallery.function_store import FunctionRegistryStore
from patchhive.gallery.sketch_store import ModuleSketchStore

from patchhive.ops.build_canonical_rig_v2 import build_canonical_rig_v2
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import suggest_layouts, CaseSpec
from patchhive.pipeline.run_library import run_library

from patchhive.ops.prune_library import prune_library, LibraryPruneSpec
from patchhive.export.export_pack import export_pack
from patchhive.export.export_library_pdf_interactive import export_library_pdf_interactive


@dataclass(frozen=True)
class AbsorbResult:
    canon_rig_id: str
    patch_count_raw: int
    patch_count_pruned: int
    out_dir: str


def absorb_rig_to_artifacts(
    rig: RigSpecV2,
    *,
    gallery_root: str,
    out_dir: str,
    preset: str = "core",
    prune_spec: Optional[LibraryPruneSpec] = None,
    interactive_pdf: bool = True,
) -> AbsorbResult:
    """
    Absorb a RigSpecV2 and generate complete patch library artifacts.

    Process:
    1. Canonicalize rig (gallery lookup + overrides)
    2. Compute metrics and suggest layouts
    3. Generate patch library
    4. Prune to target size
    5. Export PDF, SVGs, JSON
    """
    gallery = ModuleGalleryStore(gallery_root)
    fn_store = FunctionRegistryStore(gallery_root)
    sketch_store = ModuleSketchStore(gallery_root)

    # Canonicalize
    canon = build_canonical_rig_v2(rig, gallery_store=gallery)

    # Metrics + layout suggestion
    metrics = map_metrics(canon)
    layouts = suggest_layouts(
        canon,
        metrics,
        case=CaseSpec(rows=rig.case.rows, row_hp=rig.case.row_hp),
    )
    best = sorted(layouts, key=lambda l: (-l.score_breakdown.learning_gradient, -l.total_score))[0]

    # Generate library
    from patchhive.presets.library_presets import starter_preset, core_preset, deep_preset
    constraints = starter_preset() if preset == "starter" else deep_preset() if preset == "deep" else core_preset()
    lib = run_library(canon, constraints=constraints, include_diagrams=False)

    # Prune
    if prune_spec is None:
        prune_spec = LibraryPruneSpec(max_total=160, max_per_category=70, drop_runaway=True)

    lib2 = prune_library(lib, prune_spec)

    # Export
    manifest = export_pack(canon, lib2, out_dir=out_dir)

    if interactive_pdf:
        pdf_path = str(Path(out_dir) / "pdf" / "patchbook.pdf")
        export_library_pdf_interactive(canon, lib2, out_pdf=pdf_path, layout_by_patch=None)

    return AbsorbResult(
        canon_rig_id=canon.rig_id,
        patch_count_raw=len(lib.patches),
        patch_count_pruned=len(lib2.patches),
        out_dir=out_dir,
    )
