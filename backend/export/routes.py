"""
FastAPI routes for export functionality (PDF, SVG).
"""

from hashlib import sha256
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from community.models import User
from community.routes import require_auth
from core import get_db, settings
from monetization.credits import get_credits_balance
from monetization.models import CreditsLedger, Export
from patches.models import Patch
from racks.models import Rack
from runs.models import Run

from .pdf import (
    PATCHBOOK_TEMPLATE_VERSION,
    build_patchbook_pdf_bytes,
    compute_patchbook_content_hash,
    generate_patch_pdf,
    generate_rack_pdf,
)
from .visualization import generate_patch_diagram_svg, generate_rack_layout_svg
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
        waveform_params = infer_waveform_params_from_patch(patch.category, has_lfo, has_envelope)

        svg = generate_waveform_svg(waveform_params, seed=patch.generation_seed)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")


@router.post("/runs/{run_id}/patchbook")
def export_patchbook_pdf(
    run_id: int,
    force_fail: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """
    Export a patch book PDF for a run (credit gated).

    PAID FEATURE - Returns deterministic PDF with:
    - Template version header
    - Content hash for cache validation
    - Sorted patches for reproducibility
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rack = db.query(Rack).filter(Rack.id == run.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    # Compute content hash before checking cache
    patch_ids = [p.id for p in db.query(Patch).filter(Patch.rack_id == rack.id).all()]
    content_hash = compute_patchbook_content_hash(rack.id, patch_ids)

    # Check for cached export with matching content hash
    cached = (
        db.query(Export)
        .filter(
            Export.run_id == run_id,
            Export.export_type == "patchbook",
            Export.status == "completed",
            Export.manifest_hash == content_hash,
        )
        .first()
    )
    if cached:
        return {
            "export_id": cached.id,
            "status": cached.status,
            "artifact_path": (cached.provenance or {}).get("artifact_path"),
            "content_hash": content_hash,
            "template_version": PATCHBOOK_TEMPLATE_VERSION,
            "cached": True,
        }

    balance = get_credits_balance(db, current_user.id)
    if balance < settings.patchbook_export_cost:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    if force_fail and settings.test_mode:
        raise HTTPException(status_code=500, detail="Forced export failure")

    # Generate deterministic PDF to disk
    pdf_path = generate_rack_pdf(db, rack)

    export = Export(
        user_id=current_user.id,
        rack_id=rack.id,
        run_id=run.id,
        export_type="patchbook",
        status="completed",
        credits_spent=settings.patchbook_export_cost,
        manifest_hash=content_hash,
        provenance={
            "artifact_path": pdf_path,
            "template_version": PATCHBOOK_TEMPLATE_VERSION,
            "patch_count": len(patch_ids),
        },
    )
    db.add(export)
    db.commit()
    db.refresh(export)

    ledger = CreditsLedger(
        user_id=current_user.id,
        change_type="Spend",
        credits_delta=-settings.patchbook_export_cost,
        notes="Patch book export",
        export_id=export.id,
    )
    db.add(ledger)
    db.commit()

    return {
        "export_id": export.id,
        "status": export.status,
        "artifact_path": pdf_path,
        "content_hash": content_hash,
        "template_version": PATCHBOOK_TEMPLATE_VERSION,
        "cached": False,
    }
