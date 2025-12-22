"""FastAPI routes for patch generation runs."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db
from runs.models import Run
from patches.models import Patch
from patches.routes import build_patch_response
from .schemas import RunListResponse, RunPatchesResponse, RunResponse

router = APIRouter()


@router.get("/", response_model=RunListResponse)
def list_runs(
    rack_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    runs = db.query(Run).filter(Run.rack_id == rack_id).order_by(Run.created_at.desc()).all()
    return RunListResponse(total=len(runs), runs=runs)


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/patches", response_model=RunPatchesResponse)
def get_run_patches(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    patches = db.query(Patch).filter(Patch.run_id == run_id).all()
    patch_responses = [build_patch_response(db, patch) for patch in patches]
    return RunPatchesResponse(
        run_id=run_id,
        patches=patch_responses,
        total=len(patch_responses),
        created_at=run.created_at,
    )
