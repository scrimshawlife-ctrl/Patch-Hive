from __future__ import annotations

from reportlab.pdfgen import canvas


def apply_deterministic_pdf_metadata(
    c: canvas.Canvas,
    template_version: str,
    content_hash: str,
) -> None:
    c.setAuthor("PatchHive")
    c.setCreator("PatchHive PatchBook")
    c.setTitle("PatchHive PatchBook")
    c.setSubject(f"PatchHive PatchBook Template v{template_version} ({content_hash})")
