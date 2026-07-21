"""Minimal Design Engine orchestrator: compose pack from sealed compilations + recipe."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from canon.contracts import canonical_json, canonical_sha256
from export.patchbook.design.brand_policy import (
    PDF_CREATOR_PATTERN,
    scan_forbidden_strings,
)
from export.patchbook.design.content_spine import LoadedLibrary
from export.patchbook.design.layout_ir import (
    LayoutRegion,
    PageKind,
    PatchPageLayoutIR,
    composition_hash,
)
from export.patchbook.design.recipe import (
    DESIGN_ENGINE_VERSION,
    ResolvedStyleRecipe,
    recipe_hash,
)
from export.patchbook.pdf_meta import normalize_pdf_metadata


@dataclass(frozen=True)
class ComposeResult:
    composition_hash: str
    pack_manifest_hash: str
    page_count: int
    layout_irs: tuple[PatchPageLayoutIR, ...]


def compose_design_export_pack(
    library: LoadedLibrary,
    recipe: ResolvedStyleRecipe,
    *,
    out_dir: str | Path,
    export_id: str,
) -> ComposeResult:
    """Write design_export_pack.v1 directory; presentation only."""
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "style").mkdir(exist_ok=True)
    (root / "source").mkdir(exist_ok=True)
    (root / "pages" / "json").mkdir(parents=True, exist_ok=True)
    (root / "manifest").mkdir(exist_ok=True)
    (root / "technical").mkdir(exist_ok=True)

    resolved_hash = recipe_hash(recipe)
    (root / "style" / "resolved_recipe.json").write_text(
        canonical_json(recipe.model_dump(mode="json")), encoding="utf-8"
    )
    (root / "style" / "resolved_recipe.sha256").write_text(resolved_hash + "\n", encoding="utf-8")

    library_index = {
        "source_run_id": library.source_run_id,
        "source_rig_revision_id": library.source_rig_revision_id,
        "bridge_artifact_manifest_hash": library.bridge_artifact_manifest_hash,
        "library_content_hash": library.library_content_hash,
        "load_path": library.load_path,
        "patches": [
            {
                "position": item.position,
                "title": item.compilation.patch_plan.title,
                "graph_artifact_id": item.compilation.patch_graph.artifact_id,
                "canonical_hash": item.compilation.canonical_hash_value(),
                "edge_count": len(item.compilation.patch_graph.edges),
            }
            for item in library.items
        ],
    }
    (root / "source" / "library_index.json").write_text(
        canonical_json(library_index), encoding="utf-8"
    )

    layout_irs: list[PatchPageLayoutIR] = []
    # Cover
    layout_irs.append(_front_matter_page(0, "cover", recipe))
    page_index = 1
    for item in library.items:
        ir = _execution_page(page_index, item.compilation, recipe)
        layout_irs.append(ir)
        page_payload = {
            "page_index": page_index,
            "page_kind": "execution",
            "plan": item.compilation.patch_plan.canonical_dict(),
            "graph": {
                "artifact_id": item.compilation.patch_graph.artifact_id,
                "nodes": len(item.compilation.patch_graph.nodes),
                "edges": [
                    {
                        "edge_id": e.edge_id,
                        "source_port_id": e.source_port_id,
                        "target_port_id": e.target_port_id,
                        "signal_type": e.signal_type,
                    }
                    for e in item.compilation.patch_graph.edges
                ],
            },
            "validation": item.compilation.validation_report.canonical_dict(),
        }
        (root / "pages" / "json" / f"page-{page_index:04d}.json").write_text(
            canonical_json(page_payload), encoding="utf-8"
        )
        page_index += 1

    # Colophon
    layout_irs.append(_front_matter_page(page_index, "colophon", recipe))

    # Brand text scan
    brand_scan = scan_forbidden_strings(
        [recipe.notes, PDF_CREATOR_PATTERN, "PatchHive", "A Zero State Product"]
    )
    if not brand_scan.ok:
        raise ValueError(f"BRAND_POLICY_VIOLATION:{','.join(brand_scan.violations)}")

    comp_hash = composition_hash(
        library_content_hash=library.library_content_hash,
        bridge_artifact_manifest_hash=library.bridge_artifact_manifest_hash,
        resolved_recipe_hash=resolved_hash,
        layout_irs=layout_irs,
        design_engine_version=DESIGN_ENGINE_VERSION,
    )

    pdf_path = root / "PatchBook.pdf"
    _render_execution_pdf(library, recipe, pdf_path, export_id=export_id, composition_hash=comp_hash)

    # Technical companion (text-first)
    companion_lines = [
        "PatchHive Technical Companion",
        f"export_id={export_id}",
        f"composition_hash={comp_hash}",
        f"library_content_hash={library.library_content_hash}",
        f"style_recipe_hash={resolved_hash}",
        f"design_engine_version={DESIGN_ENGINE_VERSION}",
        f"mode={recipe.mode.value}",
        f"template_family={recipe.template_family.value}",
        "",
    ]
    for item in library.items:
        companion_lines.append(f"## {item.compilation.patch_plan.title}")
        companion_lines.append(item.compilation.patch_plan.intent)
        for step in item.compilation.patch_plan.steps:
            companion_lines.append(f"  [{step.phase}] {step.instruction}")
        for edge in item.compilation.patch_graph.edges:
            companion_lines.append(
                f"  CABLE {edge.edge_id}: {edge.source_port_id} -> {edge.target_port_id} ({edge.signal_type})"
            )
        companion_lines.append("")
    (root / "technical" / "companion.txt").write_text("\n".join(companion_lines), encoding="utf-8")

    if recipe.constraints.canonical_appendix_required:
        # Dual-artifact: copy execution pdf as technical appendix
        appendix = root / "technical" / "PatchBook-execution.pdf"
        appendix.write_bytes(pdf_path.read_bytes())

    manifest: dict[str, Any] = {
        "schema_version": "patchhive.design_export_pack.v1",
        "export_id": export_id,
        "design_engine_version": DESIGN_ENGINE_VERSION,
        "composition_hash": comp_hash,
        "library_content_hash": library.library_content_hash,
        "bridge_artifact_manifest_hash": library.bridge_artifact_manifest_hash,
        "style_recipe_hash": resolved_hash,
        "mode": recipe.mode.value,
        "template_family": recipe.template_family.value,
        "page_count": len(layout_irs),
        "resolved_tier": recipe.resolved_tier,
        "paths": {
            "pdf": "PatchBook.pdf",
            "companion": "technical/companion.txt",
            "library_index": "source/library_index.json",
            "resolved_recipe": "style/resolved_recipe.json",
        },
    }
    body_hash = canonical_sha256({k: v for k, v in manifest.items() if k != "pack_manifest_hash"})
    manifest["pack_manifest_hash"] = body_hash
    (root / "manifest" / "patch-book.json").write_text(canonical_json(manifest), encoding="utf-8")
    (root / "manifest" / "checksums.json").write_text(
        canonical_json({"composition_hash": comp_hash, "pack_manifest_hash": body_hash}),
        encoding="utf-8",
    )
    (root / "LICENSE.txt").write_text(
        "PatchHive export. Designed and Engineered by Zero State.\n", encoding="utf-8"
    )

    return ComposeResult(
        composition_hash=comp_hash,
        pack_manifest_hash=body_hash,
        page_count=len(layout_irs),
        layout_irs=tuple(layout_irs),
    )


def _front_matter_page(index: int, role: str, recipe: ResolvedStyleRecipe) -> PatchPageLayoutIR:
    from export.patchbook.design.layout_ir import BrandMarkRef

    region = LayoutRegion(
        region_id="identity",
        role="identity",
        required=True,
        bbox_pt=(36.0, 700.0, 540.0, 60.0),
        reading_order=0,
    )
    marks = ()
    if role in {"cover", "colophon"}:
        marks = (
            BrandMarkRef(
                mark_id="patchhive" if role == "cover" else "zero_state",
                page_role="cover" if role == "cover" else "colophon",
                bbox_pt=(36.0, 40.0, 100.0, 12.0),
                opacity=0.7,
            ),
        )
    return PatchPageLayoutIR(
        page_id=f"fm-{role}-{index}",
        page_index=index,
        page_kind=PageKind.FRONT_MATTER if role == "cover" else PageKind.BACK_MATTER,
        page_size="us_letter",
        regions=(region,),
        reading_order=("identity",),
        brand_marks=marks,
        layout_algorithm_id="orthogonal_schematic",
        fit={"role": role, "mode": recipe.mode.value},
    )


def _execution_page(index: int, compilation, recipe: ResolvedStyleRecipe) -> PatchPageLayoutIR:
    regions = (
        LayoutRegion(
            region_id="identity",
            role="identity",
            required=True,
            bbox_pt=(36.0, 720.0, 540.0, 40.0),
            reading_order=0,
        ),
        LayoutRegion(
            region_id="diagram",
            role="diagram",
            required=True,
            bbox_pt=(36.0, 400.0, 540.0, 280.0),
            reading_order=1,
        ),
        LayoutRegion(
            region_id="construction",
            role="construction",
            required=True,
            bbox_pt=(36.0, 120.0, 540.0, 260.0),
            reading_order=2,
        ),
        LayoutRegion(
            region_id="footer",
            role="footer",
            required=True,
            bbox_pt=(36.0, 36.0, 540.0, 40.0),
            reading_order=3,
        ),
    )
    return PatchPageLayoutIR(
        page_id=f"exec-{compilation.patch_graph.artifact_id}",
        page_index=index,
        page_kind=PageKind.EXECUTION,
        patch_artifact_id=compilation.patch_graph.artifact_id,
        page_size="us_letter",
        regions=regions,
        reading_order=tuple(r.region_id for r in regions),
        diagram_literal=recipe.weights.diagram_literalness >= 50,
        layout_algorithm_id="orthogonal_schematic",
        fit={"edge_count": len(compilation.patch_graph.edges)},
    )


def _render_execution_pdf(
    library: LoadedLibrary,
    recipe: ResolvedStyleRecipe,
    path: Path,
    *,
    export_id: str,
    composition_hash: str,
) -> None:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Cover
    c.setFont("Helvetica-Bold", 22)
    c.drawString(inch, height - inch, "PatchHive PatchBook")
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0.96, 0.65, 0.14)  # approx amber
    c.drawString(inch, height - 1.35 * inch, "Signal Manual · Professional")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    c.drawString(inch, height - 1.7 * inch, f"Export: {export_id}")
    c.drawString(inch, height - 1.95 * inch, f"Run: {library.source_run_id}")
    c.drawString(inch, height - 2.2 * inch, f"Composition: {composition_hash[:16]}…")
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(inch, 0.75 * inch, "A Zero State Product")
    c.setFillColorRGB(0, 0, 0)
    c.showPage()

    recipe_h = recipe_hash(recipe)
    for item in library.items:
        plan = item.compilation.patch_plan
        graph = item.compilation.patch_graph
        y = height - inch
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, y, plan.title[:80])
        y -= 18
        c.setFont("Helvetica", 9)
        c.drawString(inch, y, f"Intent: {plan.intent[:120]}")
        y -= 16
        c.setStrokeColorRGB(0.96, 0.65, 0.14)
        c.line(inch, y, width - inch, y)
        c.setStrokeColorRGB(0, 0, 0)
        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(inch, y, "Construction")
        y -= 14
        c.setFont("Helvetica", 9)
        for step in plan.steps:
            line = f"{step.position}. [{step.phase}] {step.instruction}"
            for chunk in _wrap(line, 95):
                if y < inch + 40:
                    break
                c.drawString(inch, y, chunk)
                y -= 12
        y -= 8
        c.setFont("Helvetica-Bold", 11)
        c.drawString(inch, y, "Cables")
        y -= 14
        c.setFont("Courier", 8)
        for edge in graph.edges:
            line = f"{edge.edge_id}: {edge.source_port_id} -> {edge.target_port_id} [{edge.signal_type}]"
            if y < inch + 30:
                break
            c.drawString(inch, y, line[:110])
            y -= 10
        # Execution footer
        c.setFont("Helvetica", 7)
        c.drawString(
            inch,
            0.55 * inch,
            f"{graph.artifact_id} | execution | {composition_hash[:16]} | "
            f"recipe:{recipe_h[:8]} | eng:{DESIGN_ENGINE_VERSION}",
        )
        c.drawRightString(width - inch, 0.55 * inch, f"legibility={recipe.weights.legibility}")
        c.showPage()

    # Colophon
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, height - inch, "Colophon")
    c.setFont("Helvetica", 9)
    c.drawString(inch, height - 1.4 * inch, "Designed and Engineered by Zero State")
    c.drawString(inch, height - 1.65 * inch, "PatchHive — a Zero State product")
    c.drawString(inch, height - 1.9 * inch, f"Template family: {recipe.template_family.value}")
    c.drawString(inch, height - 2.15 * inch, f"Mode: {recipe.mode.value}")
    c.showPage()

    c.setAuthor("PatchHive")
    c.setCreator(PDF_CREATOR_PATTERN)
    c.setTitle("PatchHive PatchBook")
    c.setSubject(f"PatchHive PatchBook eng={DESIGN_ENGINE_VERSION} {composition_hash[:16]}")
    c.save()
    path.write_bytes(normalize_pdf_metadata(buf.getvalue()))


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = " ".join(cur + [w])
        if len(trial) > width and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines or [""]
