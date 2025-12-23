from __future__ import annotations

from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from patchhive.render.diagram_pdf import draw_scene_pdf
from patchhive.render.diagram_scene import build_scene
from patchhive.schemas import CanonicalRig, SuggestedLayout
from patchhive.schemas_library import PatchLibrary


def export_library_pdf(
    canon: CanonicalRig,
    library: PatchLibrary,
    *,
    out_pdf: str,
    layout_by_patch: Optional[dict[str, SuggestedLayout]] = None,
) -> str:
    """
    Writes a PDF booklet.
    """
    out_path = Path(out_pdf)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out_path), pagesize=landscape(letter))
    width, height = landscape(letter)

    c.setFont("Courier-Bold", 22)
    c.drawString(32, height - 48, "PatchHive Patch Library")
    c.setFont("Courier", 12)
    c.drawString(32, height - 76, f"Rig: {canon.rig_id}")
    c.drawString(32, height - 96, f"Patches: {len(library.patches)}")
    c.drawString(
        32,
        height - 116,
        (
            f"Tier: {library.constraints.tier.value} | max_cables={library.constraints.max_cables} | "
            f"feedback={library.constraints.allow_feedback}"
        ),
    )
    c.showPage()

    c.setFont("Courier-Bold", 16)
    c.drawString(32, height - 48, "Index")
    c.setFont("Courier", 10)
    y = height - 80
    for item in library.patches[:60]:
        c.drawString(
            32,
            y,
            (
                f"{item.card.category.value} | {item.card.difficulty.value} | "
                f"{item.card.name} ({item.card.patch_id})"
            ),
        )
        y -= 14
        if y < 40:
            break
    c.showPage()

    for item in library.patches:
        title = (
            f"{item.card.name} — {item.card.category.value} / {item.card.difficulty.value} — "
            f"cables={item.card.cable_count}"
        )
        layout = layout_by_patch.get(item.card.patch_id) if layout_by_patch else None
        scene = build_scene(canon, item.patch, layout=layout)
        draw_scene_pdf(c, scene, title=title)

        c.setFont("Courier", 8)
        warn = (item.card.warnings or [])[:3]
        if warn:
            c.drawString(24, 20, "WARN: " + " | ".join(w[:120] for w in warn))
        c.showPage()

    c.save()
    return str(out_path)
