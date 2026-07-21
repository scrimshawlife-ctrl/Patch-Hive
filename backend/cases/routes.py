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
    max_hp: Optional[int] = None,
    q: Optional[str] = Query(None, description="Search brand or name"),
    format_family: Optional[str] = Query(
        None,
        description="Filter by meta.format_family (e.g. Eurorack). Applied after SQL filters.",
    ),
    powered: Optional[bool] = Query(
        None,
        description="Filter by meta.powered when present; null-power treated as powered for true.",
    ),
    min_rows: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
):
    """List cases with optional filters (SQL + lightweight meta post-filter)."""
    query = db.query(Case)

    if brand:
        query = query.filter(Case.brand.ilike(f"%{brand}%"))
    if min_hp is not None:
        query = query.filter(Case.total_hp >= min_hp)
    if max_hp is not None:
        query = query.filter(Case.total_hp <= max_hp)
    if min_rows is not None:
        query = query.filter(Case.rows >= min_rows)
    if q:
        like = f"%{q}%"
        query = query.filter((Case.brand.ilike(like)) | (Case.name.ilike(like)))

    # Cap pre-meta scan so format/powered filters stay bounded.
    candidates = query.order_by(Case.brand.asc(), Case.name.asc()).limit(2000).all()

    def _format_ok(case: Case) -> bool:
        if not format_family:
            return True
        meta = case.meta if isinstance(case.meta, dict) else {}
        family = (meta.get("format_family") or "").strip()
        # Legacy seed cases without meta default to Eurorack layout fields.
        if not family and format_family.lower() == "eurorack":
            return True
        return family.lower() == format_family.lower()

    def _powered_ok(case: Case) -> bool:
        if powered is None:
            return True
        want = bool(powered)
        meta = case.meta if isinstance(case.meta, dict) else {}
        if "powered" in meta:
            return bool(meta.get("powered")) is want
        # Without meta.powered: "No Power" / unpowered in name → unpowered; else powered.
        name_l = (case.name or "").lower()
        is_powered = "no power" not in name_l and "unpowered" not in name_l
        return is_powered is want

    filtered = [c for c in candidates if _format_ok(c) and _powered_ok(c)]
    total = len(filtered)
    cases = filtered[skip : skip + limit]

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
