"""
FastAPI routes for export functionality (PDF, SVG).
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from core import get_db
from patches.models import Patch
from racks.models import Rack
from .pdf import generate_patch_pdf, generate_rack_pdf
from .visualization import generate_rack_layout_svg, generate_patch_diagram_svg
from .waveform import generate_waveform_svg, infer_waveform_params_from_patch

router = APIRouter()


@router.get("/patches/{patch_id}/pdf")
def export_patch_pdf(patch_id: int, db: Session = Depends(get_db)):
    """Export a patch as PDF."""
    patch = db.query(Patch).filter(Patch.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")

    try:
        pdf_path = generate_patch_pdf(db, patch)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"patch_{patch.id}_{patch.name.replace(' ', '_')}.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/racks/{rack_id}/pdf")
def export_rack_pdf(rack_id: int, db: Session = Depends(get_db)):
    """Export a rack as PDF."""
    rack = db.query(Rack).filter(Rack.id == rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    try:
        pdf_path = generate_rack_pdf(db, rack)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"rack_{rack.id}_{rack.name.replace(' ', '_')}.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/racks/{rack_id}/layout.svg")
def export_rack_layout_svg(rack_id: int, db: Session = Depends(get_db)):
    """Export rack layout as SVG."""
    rack = db.query(Rack).filter(Rack.id == rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    try:
        svg = generate_rack_layout_svg(db, rack)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")


@router.get("/patches/{patch_id}/diagram.svg")
def export_patch_diagram_svg(patch_id: int, db: Session = Depends(get_db)):
    """Export patch diagram as SVG."""
    patch = db.query(Patch).filter(Patch.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")

    rack = db.query(Rack).filter(Rack.id == patch.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    try:
        svg = generate_patch_diagram_svg(db, rack, patch.connections)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")


@router.get("/patches/{patch_id}/waveform.svg")
def export_patch_waveform_svg(patch_id: int, db: Session = Depends(get_db)):
    """Export patch waveform approximation as SVG."""
    patch = db.query(Patch).filter(Patch.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")

    try:
        # Infer waveform params from patch
        has_lfo = any("lfo" in conn.get("from_port", "").lower() for conn in patch.connections)
        has_envelope = any(
            "envelope" in conn.get("from_port", "").lower() for conn in patch.connections
        )
        waveform_params = infer_waveform_params_from_patch(
            patch.category, has_lfo, has_envelope
        )

        svg = generate_waveform_svg(waveform_params, seed=patch.generation_seed)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")
