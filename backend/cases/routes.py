"""
FastAPI routes for Case management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db

from .models import Case
from .schemas import CaseCreate, CaseListResponse, CaseResponse, CaseUpdate

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=201)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    """Create a new case."""
    # Validate hp_per_row matches rows
    if len(case.hp_per_row) != case.rows:
        raise HTTPException(
            status_code=400, detail=f"hp_per_row length must match rows ({case.rows})"
        )

    # Validate total_hp matches sum of hp_per_row
    if sum(case.hp_per_row) != case.total_hp:
        raise HTTPException(
            status_code=400,
            detail=f"total_hp ({case.total_hp}) must match sum of hp_per_row ({sum(case.hp_per_row)})",
        )

    db_case = Case(
        brand=case.brand,
        name=case.name,
        total_hp=case.total_hp,
        rows=case.rows,
        hp_per_row=case.hp_per_row,
        power_12v_ma=case.power_12v_ma,
        power_neg12v_ma=case.power_neg12v_ma,
        power_5v_ma=case.power_5v_ma,
        description=case.description,
        manufacturer_url=case.manufacturer_url,
        meta=case.meta,
        source=case.source,
        source_reference=case.source_reference,
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@router.get("/", response_model=CaseListResponse)
def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    brand: Optional[str] = None,
    min_hp: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List cases with optional filters."""
    query = db.query(Case)

    # Apply filters
    if brand:
        query = query.filter(Case.brand.ilike(f"%{brand}%"))
    if min_hp is not None:
        query = query.filter(Case.total_hp >= min_hp)

    total = query.count()
    cases = query.offset(skip).limit(limit).all()

    return CaseListResponse(total=total, cases=cases)


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    """Get a specific case by ID."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(case_id: int, case_update: CaseUpdate, db: Session = Depends(get_db)):
    """Update a case."""
    db_case = db.query(Case).filter(Case.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Update fields if provided
    update_data = case_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_case, field, value)

    db.commit()
    db.refresh(db_case)
    return db_case


@router.delete("/{case_id}", status_code=204)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    """Delete a case."""
    db_case = db.query(Case).filter(Case.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")

    db.delete(db_case)
    db.commit()
    return None
