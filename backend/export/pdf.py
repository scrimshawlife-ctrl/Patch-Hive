"""
PDF export functionality for patch books.
Generates PDFs with rack layouts, patch diagrams, and waveforms.

DETERMINISM GUARANTEE:
- Same rack + patches → same PDF content hash (modulo metadata)
- Template version tracked for regression detection
- Timestamps normalized to export request time (not generation time)
"""

import io
import os
from datetime import datetime
from hashlib import sha256
from typing import Optional

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from core import settings
from patches.models import Patch
from racks.models import Rack

from .visualization import generate_patch_diagram_svg, generate_rack_layout_svg
from .waveform import generate_waveform_svg, infer_waveform_params_from_patch

# Template version - bump when PDF layout/structure changes
PATCHBOOK_TEMPLATE_VERSION = "1.0.0"


def _load_svg2rlg():
    try:
        from svglib.svglib import svg2rlg
    except ImportError as exc:
        raise RuntimeError("svglib is required for PDF exports") from exc
    return svg2rlg


def generate_patch_pdf(db: Session, patch: Patch, output_path: Optional[str] = None) -> str:
    """
    Generate a PDF for a single patch.

    Args:
        db: Database session
        patch: Patch to export
        output_path: Output file path (generated if not provided)

    Returns:
        Path to generated PDF
    """
    # Generate output path if not provided
    if output_path is None:
        os.makedirs(settings.export_dir, exist_ok=True)
        output_path = os.path.join(
            settings.export_dir, f"patch_{patch.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

    # Create canvas
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, height - inch, patch.name)

    # Metadata
    c.setFont("Helvetica", 12)
    y = height - inch - 30
    c.drawString(inch, y, f"Category: {patch.category}")
    y -= 20
    c.drawString(inch, y, f"Generation Seed: {patch.generation_seed}")
    y -= 20
    c.drawString(inch, y, f"Engine Version: {patch.generation_version}")
    y -= 40

    # Description
    if patch.description:
        c.setFont("Helvetica", 10)
        c.drawString(inch, y, f"Description: {patch.description}")
        y -= 40

    # Get rack
    rack = db.query(Rack).filter(Rack.id == patch.rack_id).first()

    # Rack layout
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Rack Layout")
    y -= 20

    try:
        svg2rlg = _load_svg2rlg()
        rack_svg = generate_rack_layout_svg(db, rack, width=int(width - 2 * inch))
        rack_svg_io = io.StringIO(rack_svg)
        rack_drawing = svg2rlg(rack_svg_io)
        if rack_drawing:
            # Scale to fit
            scale = min((width - 2 * inch) / rack_drawing.width, 200 / rack_drawing.height)
            rack_drawing.scale(scale, scale)
            rack_drawing.drawOn(c, inch, y - rack_drawing.height * scale - 20)
            y -= rack_drawing.height * scale + 40
    except Exception as e:
        c.setFont("Helvetica", 10)
        c.drawString(inch, y, f"[Rack layout could not be rendered: {e}]")
        y -= 40

    # New page for patch diagram
    c.showPage()
    y = height - inch

    # Patch diagram
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Patch Connections")
    y -= 20

    try:
        svg2rlg = _load_svg2rlg()
        patch_svg = generate_patch_diagram_svg(
            db, rack, patch.connections, width=int(width - 2 * inch), colorize_cables=False
        )
        patch_svg_io = io.StringIO(patch_svg)
        patch_drawing = svg2rlg(patch_svg_io)
        if patch_drawing:
            scale = min((width - 2 * inch) / patch_drawing.width, 300 / patch_drawing.height)
            patch_drawing.scale(scale, scale)
            patch_drawing.drawOn(c, inch, y - patch_drawing.height * scale - 20)
            y -= patch_drawing.height * scale + 40
    except Exception as e:
        c.setFont("Helvetica", 10)
        c.drawString(inch, y, f"[Patch diagram could not be rendered: {e}]")
        y -= 40

    # Waveform (if enough space, otherwise new page)
    if y < 300:
        c.showPage()
        y = height - inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Waveform Approximation")
    y -= 20

    try:
        svg2rlg = _load_svg2rlg()
        # Infer waveform params from patch
        has_lfo = any("lfo" in conn.get("from_port", "").lower() for conn in patch.connections)
        has_envelope = any(
            "envelope" in conn.get("from_port", "").lower() for conn in patch.connections
        )
        waveform_params = infer_waveform_params_from_patch(patch.category, has_lfo, has_envelope)

        waveform_svg = generate_waveform_svg(
            waveform_params, width=800, height=200, seed=patch.generation_seed
        )
        waveform_svg_io = io.StringIO(waveform_svg)
        waveform_drawing = svg2rlg(waveform_svg_io)
        if waveform_drawing:
            scale = min((width - 2 * inch) / waveform_drawing.width, 200 / waveform_drawing.height)
            waveform_drawing.scale(scale, scale)
            waveform_drawing.drawOn(c, inch, y - waveform_drawing.height * scale - 20)
    except Exception as e:
        c.setFont("Helvetica", 10)
        c.drawString(inch, y, f"[Waveform could not be rendered: {e}]")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(
        inch,
        0.5 * inch,
        f"Generated by PatchHive v{settings.app_version} on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    )

    # Save
    c.save()

    return output_path


def build_patchbook_pdf_bytes(
    db: Session, rack: Rack, export_timestamp: Optional[datetime] = None
) -> bytes:
    """
    Generate a deterministic patch book PDF as bytes (in-memory).

    This is the PAID FEATURE core function. Determinism guarantees:
    - Same rack + patches (sorted by ID) → same PDF structure
    - Timestamp is normalized to export_timestamp (not current time)
    - Template version embedded for regression tracking

    Args:
        db: Database session
        rack: Rack to export
        export_timestamp: Timestamp to embed (defaults to now, normalized for tests)

    Returns:
        PDF file as bytes
    """
    if export_timestamp is None:
        export_timestamp = datetime.now()

    # Get all patches for this rack, sorted deterministically by ID
    patches = db.query(Patch).filter(Patch.rack_id == rack.id).order_by(Patch.id).all()

    # Create in-memory buffer
    buffer = io.BytesIO()
    svg2rlg = _load_svg2rlg()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Cover page
    c.setFont("Helvetica-Bold", 32)
    c.drawString(inch, height - 2 * inch, rack.name)

    c.setFont("Helvetica", 16)
    c.drawString(inch, height - 2.5 * inch, f"Rack Configuration")
    c.drawString(inch, height - 2.8 * inch, f"{len(patches)} Patches")

    c.setFont("Helvetica", 12)
    if rack.description:
        c.drawString(inch, height - 3.2 * inch, rack.description[:100])

    c.setFont("Helvetica", 10)
    c.drawString(
        inch,
        height - 3.6 * inch,
        f"Generated: {export_timestamp.strftime('%Y-%m-%d %H:%M')}",
    )

    # Template version footer (bottom left, cover page)
    c.setFont("Helvetica", 8)
    c.drawString(inch, 0.5 * inch, f"PatchHive v{settings.app_version}")
    c.drawString(inch, 0.35 * inch, f"Template v{PATCHBOOK_TEMPLATE_VERSION}")

    c.showPage()

    # For each patch, add pages
    for i, patch in enumerate(patches):
        y = height - inch
        c.setFont("Helvetica-Bold", 20)
        c.drawString(inch, y, f"{i + 1}. {patch.name}")
        y -= 30

        c.setFont("Helvetica", 12)
        c.drawString(inch, y, f"Category: {patch.category}")
        y -= 20

        if patch.description:
            c.setFont("Helvetica", 10)
            c.drawString(inch, y, patch.description[:100])

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.read()


def compute_patchbook_content_hash(rack_id: int, patch_ids: list[int]) -> str:
    """
    Compute deterministic content hash for a patch book export.

    Hash includes:
    - Rack ID
    - Sorted patch IDs
    - Template version

    This allows cache validation and regression detection.
    """
    normalized = f"rack:{rack_id}|patches:{sorted(patch_ids)}|template:{PATCHBOOK_TEMPLATE_VERSION}"
    return sha256(normalized.encode()).hexdigest()


def generate_rack_pdf(db: Session, rack: Rack, output_path: Optional[str] = None) -> str:
    """
    Generate a PDF for a rack with all its patches (DISK MODE).

    Args:
        db: Database session
        rack: Rack to export
        output_path: Output file path (generated if not provided)

    Returns:
        Path to generated PDF
    """
    # Generate output path if not provided
    if output_path is None:
        os.makedirs(settings.export_dir, exist_ok=True)
        output_path = os.path.join(
            settings.export_dir, f"rack_{rack.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

    # Use deterministic in-memory builder
    pdf_bytes = build_patchbook_pdf_bytes(db, rack)

    # Write to disk
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return output_path
