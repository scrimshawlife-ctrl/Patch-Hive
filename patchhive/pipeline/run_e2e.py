from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.schemas import RigSpec
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.gallery.function_store import FunctionRegistryStore
from patchhive.gallery.sketch_store import ModuleSketchStore

from patchhive.vision.gemini_interface import GeminiVisionClient
from patchhive.ops.vision_to_rigspec import vision_to_rigspec

from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import suggest_layouts, CaseSpec

from patchhive.presets.library_presets import starter_preset, core_preset, deep_preset
from patchhive.pipeline.run_library import run_library

from patchhive.ops.prune_library import prune_library, LibraryPruneSpec

from patchhive.export.export_pack import export_pack
from patchhive.export.export_library_pdf_interactive import export_library_pdf_interactive

from patchhive.render.diagram_scene import build_scene


def _pick_constraints(name: str):
    n = (name or "core").lower()
    if n == "starter":
        return starter_preset()
    if n == "deep":
        return deep_preset()
    return core_preset()


def _export_svg(scene: dict, out_path: str) -> None:
    """
    Simple SVG export from scene dictionary.
    """
    width = scene["width"]
    height = scene["height"]

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '  <style>',
        '    .module { fill: #f0f0f0; stroke: #333; stroke-width: 2; }',
        '    .jack { fill: #333; r: 4; }',
        '    .cable { fill: none; stroke-width: 2; }',
        '    .label { font-family: monospace; font-size: 10px; fill: #333; }',
        '  </style>',
    ]

    # Draw modules
    for mod in scene["modules"]:
        x, y, w, h = mod["x"], mod["y"], mod["w"], mod["h"]
        svg_lines.append(f'  <rect class="module" x="{x}" y="{y}" width="{w}" height="{h}"/>')

        # Draw jacks
        for jack_key, (jx, jy, label) in mod["jacks"].items():
            svg_lines.append(f'  <circle class="jack" cx="{jx}" cy="{jy}"/>')

    # Draw cables
    from patchhive.render.diagram_scene import CABLE_COLOR
    for cable in scene["cables"]:
        cable_type = cable["type"]
        color = CABLE_COLOR.get(cable_type, "#666")
        points = cable["points"]
        path = f'M {points[0][0]} {points[0][1]}'
        for px, py in points[1:]:
            path += f' L {px} {py}'
        svg_lines.append(f'  <path class="cable" d="{path}" stroke="{color}"/>')

    svg_lines.append('</svg>')

    Path(out_path).write_text('\n'.join(svg_lines), encoding='utf-8')


def _fallback_layout(canon):
    """Simple fallback layout for patches without a specific layout."""
    from patchhive.schemas import LayoutPlacement

    class _Layout:
        def __init__(self, placements):
            self.placements = placements

    placements = []
    x_hp = 0
    for mod in canon.modules:
        placements.append(LayoutPlacement(instance_id=mod.instance_id, row=0, x_hp=x_hp))
        x_hp += mod.hp
    return _Layout(placements)


def run_e2e(
    *,
    image_ref: str,
    rig_id: str,
    config: E2EConfig,
    gemini: GeminiVisionClient,
) -> dict:
    """
    End-to-end artifact builder.
    Deterministic core, with a single external boundary: GeminiVisionClient.extract_rig()
    """
    # --- stores
    gallery = ModuleGalleryStore(config.gallery_root)
    fn_store = FunctionRegistryStore(config.gallery_root)
    sketch_store = ModuleSketchStore(config.gallery_root)

    # --- 1) Vision extract (overlay boundary)
    vision = gemini.extract_rig(image_ref, rig_id=rig_id)

    # --- 2) Vision -> RigSpec (+ gallery enrichment + function discovery + sketches)
    def lookup(name: str, manufacturer: str | None):
        return gallery.find_by_name(name=name, manufacturer=manufacturer)

    def upsert(entry):
        gallery.append_revision(entry)

    rig: RigSpec = vision_to_rigspec(
        vision,
        gallery_lookup_fn=lookup,
        gallery_upsert_fn=upsert,
        function_store=fn_store,
        sketch_store=sketch_store,
    )

    # persist rigspec
    out_root = Path(config.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    rig_path = out_root / "rigspec.json"

    # Serialize RigSpec (dataclass) to JSON
    rig_dict = {
        "rig_id": rig.rig_id,
        "name": rig.name,
        "source": rig.source.value,
        "modules": [
            {
                "instance_id": m.instance_id,
                "gallery_module_id": m.gallery_module_id,
                "gallery_rev": m.gallery_rev.isoformat() if m.gallery_rev else None,
                "observed_placement": m.observed_placement,
            }
            for m in rig.modules
        ],
        "normalled_edges": [
            {
                "from_jack": e.from_jack,
                "to_jack": e.to_jack,
                "behavior": e.behavior.value,
            }
            for e in rig.normalled_edges
        ],
        "notes": list(rig.notes),
    }
    rig_path.write_text(json.dumps(rig_dict, indent=2, sort_keys=True), encoding="utf-8")

    # --- 3) RigSpec -> CanonicalRig
    canon = build_canonical_rig(rig, gallery_store=gallery)

    # --- 4) Metrics + suggested layout
    metrics = map_metrics(canon)
    layouts = suggest_layouts(
        canon,
        metrics,
        case=CaseSpec(rows=config.rows, row_hp=config.row_hp),
    )
    best = sorted(
        layouts,
        key=lambda l: (-l.score_breakdown.learning_gradient, -l.total_score, l.layout_type.value),
    )[0]

    # --- 5) Generate library with preset constraints
    constraints = _pick_constraints(config.preset)
    lib = run_library(canon, constraints=constraints, include_diagrams=False)

    # --- 6) Prune / shape into a real book
    prune_spec = LibraryPruneSpec(
        max_total=config.max_total,
        max_per_category=config.max_per_category,
        category_weights=config.category_weights,
        difficulty_weights=config.difficulty_weights,
        drop_runaway=config.drop_runaway,
        drop_silence=config.drop_silence,
    )
    lib2 = prune_library(lib, prune_spec)

    # --- 7) Export pack (JSON)
    manifest = export_pack(
        canon,
        lib2,
        out_dir=config.out_dir,
    )

    # --- 8) Export SVGs if requested
    if config.include_svgs:
        svg_dir = out_root / "svgs"
        svg_dir.mkdir(parents=True, exist_ok=True)

        for item in lib2.patches:
            scene = build_scene(canon, item.patch, layout=best)
            svg_path = svg_dir / f"{item.card.patch_id}.svg"
            _export_svg(scene, str(svg_path))

    # --- 9) Export PDF if requested
    if config.include_pdf and config.interactive_pdf:
        pdf_path = str(out_root / "pdf" / "patchbook.pdf")
        export_library_pdf_interactive(
            canon,
            lib2,
            out_pdf=pdf_path,
            layout_by_patch=None,
        )

    # --- 10) Compute hashes for manifest
    hashes = {}

    # Hash rigspec
    if rig_path.exists():
        hashes["rigspec.json"] = hashlib.sha256(rig_path.read_bytes()).hexdigest()[:16]

    # Hash library
    lib_path = out_root / "json" / "library.json"
    if lib_path.exists():
        hashes["library.json"] = hashlib.sha256(lib_path.read_bytes()).hexdigest()[:16]

    # Hash PDF
    pdf_path_obj = out_root / "pdf" / "patchbook.pdf"
    if pdf_path_obj.exists():
        hashes["patchbook.pdf"] = hashlib.sha256(pdf_path_obj.read_bytes()).hexdigest()[:16]

    manifest["hashes"] = hashes

    # Write enhanced manifest
    (out_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    # Write a small "summary.json" for UI
    summary = {
        "rig_id": canon.rig_id,
        "rigspec_path": "rigspec.json",
        "patch_count_raw": len(lib.patches),
        "patch_count_pruned": len(lib2.patches),
        "best_layout_type": best.layout_type.value,
        "out_dir": config.out_dir,
        "manifest_path": "manifest.json",
    }
    (out_root / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return manifest
