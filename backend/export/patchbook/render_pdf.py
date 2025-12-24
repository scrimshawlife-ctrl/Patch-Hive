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
    c.drawString(inch + 220, 0.55 * inch, f"Tier: {document.tier_name}")
    c.drawRightString(width - inch, 0.55 * inch, f"Page {page_index + 1} of {total_pages}")
    if content_hash:
        c.setFont("Helvetica", 6)
        c.drawString(inch, 0.38 * inch, f"Content Hash: {content_hash}")
    if document.tier_name == "free":
        c.setFont("Helvetica-Bold", 24)
        c.setFillColorRGB(0.85, 0.85, 0.85)
        c.saveState()
        c.translate(width / 2, 0.4 * inch)
        c.rotate(15)
        c.drawCentredString(0, 0, "PREVIEW")
        c.restoreState()
        c.setFillColorRGB(0, 0, 0)


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
    variant_lines = []
    for variant in page.variants:
        variant_lines.append(f"{variant.variant_type.upper()}: {variant.behavioral_delta_summary}")
        if variant.wiring_diff:
            variant_lines.append("Wiring diff:")
            for delta in variant.wiring_diff[:3]:
                variant_lines.append(
                    f"- {delta.action} {delta.from_module} {delta.from_port} -> {delta.to_module} {delta.to_port}"
                )
        if variant.parameter_deltas:
            variant_lines.append("Parameter deltas:")
            for delta in variant.parameter_deltas[:3]:
                variant_lines.append(
                    f"- {delta.module_name} {delta.parameter}: {delta.from_value} → {delta.to_value}"
                )
    return _draw_lines(c, variant_lines, x, y, font_size=8)


def _render_patch_fingerprint(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    if not page.patch_fingerprint:
        return y
    fingerprint = page.patch_fingerprint
    y = _draw_section_title(c, "Patch Fingerprint", x, y)
    lines = [
        f"Topology Hash: {fingerprint.topology_hash[:16]}",
        f"Cable count: {fingerprint.complexity_vector.cable_count}",
        f"Unique jacks: {fingerprint.complexity_vector.unique_jack_count}",
        f"Mod sources: {fingerprint.complexity_vector.modulation_source_count}",
        f"Probability loci: {fingerprint.complexity_vector.probability_locus_count}",
        f"Feedback: {'Yes' if fingerprint.complexity_vector.feedback_present else 'No'}",
        f"Rack fit score: {fingerprint.rack_fit_score}" if fingerprint.rack_fit_score is not None else None,
        (
            "Roles: "
            f"T{fingerprint.dominant_roles.time}% "
            f"V{fingerprint.dominant_roles.voice}% "
            f"M{fingerprint.dominant_roles.modulation}% "
            f"P{fingerprint.dominant_roles.probability}% "
            f"G{fingerprint.dominant_roles.gesture}%"
        ),
    ]
    lines = [line for line in lines if line]
    return _draw_lines(c, lines, x, y, font_size=8)


def _render_stability_envelope(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    if not page.stability_envelope:
        return y
    envelope = page.stability_envelope
    y = _draw_section_title(c, "Stability Envelope", x, y)
    lines = [f"Class: {envelope.stability_class}"]
    if envelope.primary_instability_sources:
        lines.append("Instability sources: " + ", ".join(envelope.primary_instability_sources))
    lines.extend([f"Safe start: {item}" for item in envelope.safe_start_ranges])
    lines.extend([f"Recovery: {item}" for item in envelope.recovery_procedure])
    return _draw_lines(c, lines, x, y, font_size=8)


def _render_troubleshooting_tree(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    if not page.troubleshooting_tree:
        return y
    tree = page.troubleshooting_tree
    y = _draw_section_title(c, "Troubleshooting Tree", x, y)
    lines = []
    for title, items in (
        ("No sound", tree.no_sound_checks),
        ("No modulation", tree.no_modulation_checks),
        ("Timing instability", tree.timing_instability_checks),
        ("Gain staging", tree.gain_staging_checks),
    ):
        if items:
            lines.append(f"{title}:")
            lines.extend([f"- {item}" for item in items])
    return _draw_lines(c, lines, x, y, font_size=8)


def _render_performance_macros(page: PatchBookPage, c: canvas.Canvas, x: float, y: float) -> float:
    if not page.performance_macros:
        return y
    y = _draw_section_title(c, "Performance Macros", x, y)
    lines = []
    for macro in page.performance_macros:
        lines.append(f"{macro.macro_id}: {macro.expected_effect}")
        lines.append(f"Controls: {', '.join(macro.controls_involved)}")
        lines.append(f"Safe bounds: {macro.safe_bounds} ({macro.risk_level})")
    return _draw_lines(c, lines, x, y, font_size=8)


def _render_book_insights(document: PatchBookDocument, c: canvas.Canvas) -> bool:
    if not (document.golden_rack_arrangement or document.compatibility_report or document.learning_path):
        return False
    _, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, height - inch, "PatchBook Insights")
    y = height - 1.3 * inch

    if document.golden_rack_arrangement:
        arrangement = document.golden_rack_arrangement
        y = _draw_section_title(c, "Golden Rack Arrangement", inch, y)
        for layout in arrangement.layouts:
            y = _draw_lines(c, [f"Layout {layout.layout_id} score: {layout.score}"], inch, y, font_size=9)
        y = _draw_lines(c, arrangement.scoring_explanation, inch, y, font_size=8)
        y = _draw_lines(c, [arrangement.adjacency_heatmap_summary], inch, y, font_size=8)
        if arrangement.missing_utility_warnings:
            y = _draw_lines(c, arrangement.missing_utility_warnings, inch, y, font_size=8)
        y -= 6

    if document.compatibility_report:
        report = document.compatibility_report
        y = _draw_section_title(c, "Compatibility & Gap Report", inch, y)
        if report.required_missing_utilities:
            missing = ", ".join(report.required_missing_utilities)
            y = _draw_lines(c, [f"Missing utilities: {missing}"], inch, y, font_size=8)
        if report.workaround_suggestions:
            y = _draw_lines(c, ["Workarounds:"] + report.workaround_suggestions, inch, y, font_size=8)
        if report.patch_compatibility_warnings:
            y = _draw_lines(c, ["Warnings:"] + report.patch_compatibility_warnings, inch, y, font_size=8)
        y -= 6

    if document.learning_path:
        path = document.learning_path
        y = _draw_section_title(c, "Learning Path", inch, y)
        for step in path.ordered_patch_sequence:
            y = _draw_lines(
                c,
                [f"{step.patch_name}: {step.concept} (effort {step.effort_score})"],
                inch,
                y,
                font_size=8,
            )
        y = _draw_lines(c, [f"Effort progression: {path.effort_score_progression}"], inch, y, font_size=8)
    return True


def build_patchbook_pdf_bytes(document: PatchBookDocument) -> bytes:
    """Build PatchBook PDF in-memory bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, invariant=1)
    apply_deterministic_pdf_metadata(
        c,
        document.branding.template_version,
        document.content_hash or "",
    )

    has_insights = bool(document.golden_rack_arrangement or document.compatibility_report or document.learning_path)
    total_pages = len(document.pages) + (1 if has_insights else 0)
    for idx, page in enumerate(document.pages):
        y = _page_header(c, page, document.branding.wordmark_svg)
        left_column_x = inch
        right_column_x = 4.2 * inch

        y_left = _render_module_inventory(page, c, left_column_x, y)
        y_left = _render_io_inventory(page, c, left_column_x, y_left - 8)
        y_left = _render_parameter_snapshot(page, c, left_column_x, y_left - 8)

        y_right = _render_schematic(page, c, right_column_x, y)
        y_right = _render_patching_order(page, c, right_column_x, y_right - 8)
        y_right = _render_patch_fingerprint(page, c, right_column_x, y_right - 8)
        y_right = _render_stability_envelope(page, c, right_column_x, y_right - 8)
        y_right = _render_troubleshooting_tree(page, c, right_column_x, y_right - 8)
        y_right = _render_performance_macros(page, c, right_column_x, y_right - 8)
        y_right = _render_variants(page, c, right_column_x, y_right - 8)

        _page_footer(c, document, idx, total_pages)
        if idx < total_pages - 1:
            c.showPage()

    if has_insights:
        _render_book_insights(document, c)
        _page_footer(c, document, total_pages - 1, total_pages)
    c.save()
    buffer.seek(0)
    return buffer.read()
