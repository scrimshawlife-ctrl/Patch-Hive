"""
FastAPI routes for Run management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db
from racks.models import Rack
from .models import Run
from .schemas import RunResponse, RunListResponse, RunCreate

router = APIRouter()


@router.post("/", response_model=RunResponse, status_code=201)
def create_run(run: RunCreate, db: Session = Depends(get_db)):
    """Create a new run record for a rack."""
    rack = db.query(Rack).filter(Rack.id == run.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    status = run.status or "queued"
    db_run = Run(rack_id=run.rack_id, status=status)
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


@router.get("/", response_model=RunListResponse)
def list_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rack_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List runs with optional filters."""
    query = db.query(Run)
    if rack_id is not None:
        query = query.filter(Run.rack_id == rack_id)

    total = query.count()
    runs = query.order_by(Run.created_at.desc()).offset(skip).limit(limit).all()

    return RunListResponse(total=total, runs=runs)
