"""FastAPI routes for patch generation runs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db
from patches.models import Patch
from patches.routes import build_patch_response
from runs.listing import build_run_response, list_runs_for_rack
from runs.models import Run

from .schemas import RunListResponse, RunPatchesResponse, RunResponse

router = APIRouter()


@router.get("/", response_model=RunListResponse)
def list_runs(
    rack_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    payload = list_runs_for_rack(db, rack_id)
    db.commit()
    return payload


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    response = build_run_response(db, run)
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
