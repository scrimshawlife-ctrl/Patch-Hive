"""FastAPI routes for patch generation runs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db
from patches.models import Patch
from patches.routes import build_patch_response
from runs.bridge import ensure_legacy_run_export_bridge
from runs.models import Run

from .schemas import RunListResponse, RunPatchesResponse, RunResponse

router = APIRouter()


def _run_response(db: Session, run: Run) -> RunResponse:
    bridge = ensure_legacy_run_export_bridge(db, run)
    return RunResponse(
        id=int(run.id),  # type: ignore[arg-type]
        rack_id=int(run.rack_id),  # type: ignore[arg-type]
        status=str(run.status),
        created_at=run.created_at,  # type: ignore[arg-type]
        rig_revision_id=bridge.rig_revision_id,
        source_run_id=bridge.source_run_id,
        artifact_manifest_hash=bridge.artifact_manifest_hash,
        export_bridge_ready=bridge.export_bridge_ready,
    )


@router.get("/", response_model=RunListResponse)
def list_runs(
    rack_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    runs = db.query(Run).filter(Run.rack_id == rack_id).order_by(Run.created_at.desc()).all()
    payload = [_run_response(db, run) for run in runs]
    db.commit()
    return RunListResponse(total=len(payload), runs=payload)


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    response = _run_response(db, run)
    db.commit()
    return response


@router.get("/{run_id}/patches", response_model=RunPatchesResponse)
def get_run_patches(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    patches = db.query(Patch).filter(Patch.run_id == run_id).all()
    return RunPatchesResponse(
        total=len(patches), patches=[build_patch_response(db, p) for p in patches]
    )
