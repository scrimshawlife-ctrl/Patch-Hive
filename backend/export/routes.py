"""
FastAPI routes for export functionality (PDF, SVG).
"""

from datetime import datetime
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

from .pdf import generate_patch_pdf, generate_rack_pdf
from .visualization import generate_patch_diagram_svg, generate_rack_layout_svg
from .patchbook.build import build_patchbook_pdf_bytes_from_payload
from .patchbook.models import PatchBookExportRequest, PATCHBOOK_TEMPLATE_VERSION, PatchBookTier

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


@router.post("/runs/{run_id}/patchbook")
def export_patchbook_pdf(
    run_id: int,
    force_fail: bool = Query(False),
    tier: PatchBookTier = Query(PatchBookTier.CORE),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Export a patch book PDF for a run (credit gated)."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    cached = (
        db.query(Export)
        .filter(
            Export.run_id == run_id, Export.export_type == "patchbook", Export.status == "completed"
        )
        .first()
    )
    if cached:
        return {
            "export_id": cached.id,
            "status": cached.status,
            "artifact_path": (cached.provenance or {}).get("artifact_path"),
            "content_hash": cached.manifest_hash,
            "template_version": PATCHBOOK_TEMPLATE_VERSION,
            "cached": True,
        }

    balance = get_credits_balance(db, current_user.id)
    if balance < settings.patchbook_export_cost:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    if force_fail and settings.test_mode:
        raise HTTPException(status_code=500, detail="Forced export failure")

    rack = db.query(Rack).filter(Rack.id == run.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    patches = (
        db.query(Patch)
        .filter(Patch.run_id == run.id)
        .order_by(Patch.id.asc())
        .all()
    )
    if not patches:
        raise HTTPException(status_code=404, detail="No patches available for run")

    payload = PatchBookExportRequest(
        rack_id=rack.id, patch_ids=[patch.id for patch in patches], tier=tier
    )
    try:
        pdf_bytes, content_hash = build_patchbook_pdf_bytes_from_payload(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    export_dir = Path(settings.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    pdf_path = export_dir / f"patchbook_run_{run.id}_{timestamp}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    digest = sha256(pdf_bytes).hexdigest()

    export = Export(
        user_id=current_user.id,
        rack_id=rack.id,
        run_id=run.id,
        export_type="patchbook",
        status="completed",
        credits_spent=settings.patchbook_export_cost,
        manifest_hash=content_hash,
        provenance={
            "artifact_path": str(pdf_path),
            "content_hash": content_hash,
            "template_version": PATCHBOOK_TEMPLATE_VERSION,
            "file_hash": digest,
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
        "artifact_path": str(pdf_path),
        "content_hash": content_hash,
        "template_version": PATCHBOOK_TEMPLATE_VERSION,
        "cached": False,
    }


@router.post("/patchbook")
def export_patchbook_document(payload: PatchBookExportRequest, db: Session = Depends(get_db)):
    """Export PatchBook PDF bytes for a rack/patch selection."""
    if not payload.rack_id and not payload.patch_ids:
        raise HTTPException(status_code=400, detail="rack_id or patch_ids required")

    rack = None
    patches_query = db.query(Patch)
    if payload.patch_ids:
        patches_query = patches_query.filter(Patch.id.in_(payload.patch_ids))
        patches = patches_query.all()
        if not patches:
            raise HTTPException(status_code=404, detail="Patches not found")
        rack_id = payload.rack_id or patches[0].rack_id
        rack = db.query(Rack).filter(Rack.id == rack_id).first()
    else:
        rack = db.query(Rack).filter(Rack.id == payload.rack_id).first()
        patches = db.query(Patch).filter(Patch.rack_id == payload.rack_id).all()

    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")
    if not patches:
        raise HTTPException(status_code=404, detail="No patches available for rack")

    try:
        pdf_bytes, content_hash = build_patchbook_pdf_bytes_from_payload(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "X-PatchBook-Template-Version": PATCHBOOK_TEMPLATE_VERSION,
            "X-PatchBook-Content-Hash": content_hash,
        },
    )
