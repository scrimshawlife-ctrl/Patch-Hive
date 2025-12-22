from __future__ import annotations

from pathlib import Path
from typing import Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter

from patchhive.schemas import CanonicalRig, LayoutPlacement
from patchhive.schemas_library import PatchLibrary
from patchhive.render.diagram_scene import build_scene
from patchhive.render.diagram_pdf import draw_scene_pdf


class _FallbackLayout:
    def __init__(self, placements):
        self.placements = placements


def _fallback_layout(canon: CanonicalRig) -> _FallbackLayout:
    placements = []
    x_hp = 0
    for mod in canon.modules:
        placements.append(LayoutPlacement(instance_id=mod.instance_id, row=0, x_hp=x_hp))
        x_hp += mod.hp
    return _FallbackLayout(placements)

def export_library_pdf_interactive(
    canon: CanonicalRig,
    library: PatchLibrary,
    *,
    out_pdf: str,
    layout_by_patch: Optional[dict] = None,  # patch_id -> SuggestedLayout
) -> str:
    """
    PDF booklet with clickable index:
      - Cover (page 1)
      - Index (page 2) -> links to patch pages (page 3+)
      - Each patch page has a named destination.
    """
    out_path = Path(out_pdf)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out_path), pagesize=landscape(letter))
    W, H = landscape(letter)

    # page numbers:
    # 1 = cover
    # 2 = index
    # 3.. = patches
    first_patch_page = 3
    _ = first_patch_page

    # --- Cover
    c.setFont("Courier-Bold", 22)
    c.drawString(32, H - 48, "PatchHive Patch Library")
    c.setFont("Courier", 12)
    c.drawString(32, H - 76, f"Rig: {canon.rig_id}")
    c.drawString(32, H - 96, f"Patches: {len(library.patches)}")
    c.drawString(
        32,
        H - 116,
        (
            f"Tier: {library.constraints.tier.value} | max_cables={library.constraints.max_cables} "
            f"| feedback={library.constraints.allow_feedback}"
        ),
    )
    c.showPage()

    # --- Index page (we draw links now; destinations created later are OK in ReportLab)
    c.setFont("Courier-Bold", 16)
    c.drawString(32, H - 48, "Index (click a patch)")
    c.setFont("Courier", 10)

    # index rows
    y = H - 80
    row_h = 14
    idx_limit = min(80, len(library.patches))

    for i in range(idx_limit):
        it = library.patches[i]
        text = f"{i+1:03d} | {it.card.category.value} | {it.card.difficulty.value} | {it.card.name}"
        c.drawString(32, y, text)

        # clickable rectangle linking to the destination name
        dest_name = f"patch:{it.card.patch_id}"
        # linkRect parameters: (contents, destinationname, Rect, relative=0)
        c.linkRect(
            contents=text,
            destinationname=dest_name,
            Rect=(28, y - 2, W - 28, y + row_h - 2),
            relative=0,
            thickness=0,
        )

        y -= row_h
        if y < 50:
            break

    c.showPage()

    # --- Patch pages
    for it in library.patches:
        dest_name = f"patch:{it.card.patch_id}"
        c.bookmarkPage(dest_name)  # named destination
        c.addOutlineEntry(it.card.name, dest_name, level=0, closed=False)

        title = (
            f"{it.card.name} — {it.card.category.value} / {it.card.difficulty.value} "
            f"— cables={it.card.cable_count}"
        )
        lay = layout_by_patch.get(it.card.patch_id) if layout_by_patch else None
        scene = build_scene(canon, it.patch, layout=lay or _fallback_layout(canon))
        draw_scene_pdf(c, scene, title=title)

        # warnings footer
        c.setFont("Courier", 8)
        warn = (it.card.warnings or [])[:3]
        if warn:
            c.drawString(24, 20, "WARN: " + " | ".join(w[:120] for w in warn))

        c.showPage()

    c.save()
    return str(out_path)
