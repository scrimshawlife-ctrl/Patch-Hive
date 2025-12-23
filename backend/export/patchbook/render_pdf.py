"""PatchBook PDF renderer."""

from __future__ import annotations

import io
from typing import Iterable

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .models import PatchBookDocument, PatchBookPage
from .pdf_meta import apply_deterministic_pdf_metadata


def _load_svg2rlg():
    try:
        from svglib.svglib import svg2rlg
    except ImportError as exc:
        raise RuntimeError("svglib is required for PatchBook exports") from exc
    return svg2rlg


def _draw_wordmark(c: canvas.Canvas, svg_text: str | None, x: float, y: float) -> None:
    if not svg_text:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y + 10, "PatchHive")
        return
    svg2rlg = _load_svg2rlg()
    drawing = svg2rlg(io.StringIO(svg_text))
    if not drawing:
        return
    scale = min(1.0, 140 / drawing.width)
    drawing.scale(scale, scale)
    drawing.drawOn(c, x, y)


def _draw_section_title(c: canvas.Canvas, title: str, x: float, y: float) -> float:
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, title)
    return y - 14


def _draw_lines(c: canvas.Canvas, lines: Iterable[str], x: float, y: float, font_size: int = 9) -> float:
    c.setFont("Helvetica", font_size)
    for line in lines:
        c.drawString(x, y, line)
        y -= font_size + 4
    return y


def _page_header(c: canvas.Canvas, page: PatchBookPage, branding_svg: str | None) -> float:
    width, height = letter
    _draw_wordmark(c, branding_svg, inch, height - 1.1 * inch)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, height - 1.3 * inch, page.header.title)
    c.setFont("Helvetica", 9)
    c.drawString(inch, height - 1.55 * inch, f"Patch ID: {page.header.patch_id}")
    c.drawString(
        inch + 140,
        height - 1.55 * inch,
        f"Rack: {page.header.rack_name} (#{page.header.rack_id})",
    )
    return height - 1.8 * inch


def _page_footer(c: canvas.Canvas, document: PatchBookDocument, page_index: int, total_pages: int) -> None:
    width, _ = letter
    c.setFont("Helvetica", 8)
    template = document.branding.template_version
    content_hash = document.content_hash or ""
    c.drawString(inch, 0.55 * inch, f"PatchHive PatchBook Template v{template}")
    c.drawRightString(width - inch, 0.55 * inch, f"Page {page_index + 1} of {total_pages}")
    if content_hash:
        c.setFont("Helvetica", 6)
        c.drawString(inch, 0.38 * inch, f"Content Hash: {content_hash}")


def _render_module_inventory(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    y = _draw_section_title(c, "Module Inventory", x, y)
    modules = [
        f"{item.brand} {item.name} ({item.hp}HP) @ row {item.row_index} hp {item.start_hp}"
        for item in page.module_inventory
    ]
    if not modules:
        modules = ["No modules recorded."]
    return _draw_lines(c, modules, x, y)


def _render_io_inventory(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    y = _draw_section_title(c, "I/O Inventory", x, y)
    endpoints = [
        f"{endpoint.module_name} {endpoint.port_name} ({endpoint.direction})"
        for endpoint in page.io_inventory
    ]
    if not endpoints:
        endpoints = ["No I/O endpoints recorded."]
    return _draw_lines(c, endpoints, x, y)


def _render_parameter_snapshot(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    y = _draw_section_title(c, "Parameter Snapshot", x, y)
    params = [
        f"{snapshot.module_name} {snapshot.parameter}: {snapshot.value}"
        for snapshot in page.parameter_snapshot
    ]
    if not params:
        params = ["No parameter snapshot available."]
    return _draw_lines(c, params, x, y)


def _render_schematic(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    y = _draw_section_title(c, "Patch Schematic", x, y)
    if page.schematic.diagram_svg:
        svg2rlg = _load_svg2rlg()
        drawing = svg2rlg(io.StringIO(page.schematic.diagram_svg))
        if drawing:
            max_width = 6.5 * inch
            max_height = 2.5 * inch
            scale = min(max_width / drawing.width, max_height / drawing.height, 1.0)
            drawing.scale(scale, scale)
            drawing.drawOn(c, x, y - drawing.height * scale)
            return y - drawing.height * scale - 12
    return _render_wiring_list(page, c, x, y)


def _render_wiring_list(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    y = _draw_section_title(c, "Wiring List", x, y)
    wiring = [
        f"{conn.from_module} {conn.from_port} -> {conn.to_module} {conn.to_port} ({conn.cable_type})"
        for conn in page.schematic.wiring_list
    ]
    if not wiring:
        wiring = ["No wiring connections recorded."]
    return _draw_lines(c, wiring, x, y, font_size=8)


def _render_patching_order(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    y = _draw_section_title(c, "Patching Order (Step 0-6)", x, y)
    for step in page.patching_order.steps:
        lines = [
            f"Step {step.step}: {step.action}",
            f"Expected: {step.expected_behavior}",
            f"Fail-fast: {step.fail_fast_check}",
        ]
        y = _draw_lines(c, lines, x, y, font_size=8)
        y -= 2
    return y


def _render_variants(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    if not page.variants:
        return y
    y = _draw_section_title(c, "Variants", x, y)
    variant_lines = [f"{variant.name}: {variant.description or ''}" for variant in page.variants]
    return _draw_lines(c, variant_lines, x, y, font_size=8)


def build_patchbook_pdf_bytes(document: PatchBookDocument) -> bytes:
    """Build PatchBook PDF in-memory bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, invariant=1)
    apply_deterministic_pdf_metadata(
        c,
        document.branding.template_version,
        document.content_hash or "",
    )

    total_pages = len(document.pages)
    for idx, page in enumerate(document.pages):
        y = _page_header(c, page, document.branding.wordmark_svg)
        left_column_x = inch
        right_column_x = 4.2 * inch

        y_left = _render_module_inventory(page, c, left_column_x, y)
        y_left = _render_io_inventory(page, c, left_column_x, y_left - 8)
        y_left = _render_parameter_snapshot(page, c, left_column_x, y_left - 8)

        y_right = _render_schematic(page, c, right_column_x, y)
        y_right = _render_patching_order(page, c, right_column_x, y_right - 8)
        y_right = _render_variants(page, c, right_column_x, y_right - 8)

        _page_footer(c, document, idx, total_pages)
        if idx < total_pages - 1:
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.read()
