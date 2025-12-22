"""
FastAPI routes for Rack management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import (
    get_db,
    generate_rig_suggested_name,
    hash_string_to_seed,
)
from cases.models import Case
from modules.models import Module
from .models import Rack, RackModule
from .schemas import RackCreate, RackUpdate, RackResponse, RackListResponse
from .validation import validate_rack_configuration

router = APIRouter()


@router.post("/", response_model=RackResponse, status_code=201)
def create_rack(rack: RackCreate, db: Session = Depends(get_db)):
    """Create a new rack with validation."""
    # For now, use a placeholder user_id (will be replaced with auth)
    user_id = 1

    # Validate rack configuration
    is_valid, errors = validate_rack_configuration(db, rack.case_id, rack.modules)
    if not is_valid:
        raise HTTPException(
            status_code=400, detail={"message": "Rack validation failed", "errors": errors}
        )

    modules = []
    for module_spec in rack.modules:
        module = db.query(Module).filter(Module.id == module_spec.module_id).first()
        if module:
            modules.append(module)

    seed = rack.generation_seed or hash_string_to_seed(f"rack-{user_id}-{rack.case_id}")
    suggested_name = rack.name_suggested or generate_rig_suggested_name(modules)
    if not rack.name:
        rack.name = suggested_name

    # Create rack
    db_rack = Rack(
        user_id=user_id,
        case_id=rack.case_id,
        name=rack.name,
        name_suggested=suggested_name,
        description=rack.description,
        tags=rack.tags,
        is_public=rack.is_public,
        generation_seed=seed,
    )
    db.add(db_rack)
    db.flush()  # Get rack.id

    # Add modules
    for module_spec in rack.modules:
        db_rack_module = RackModule(
            rack_id=db_rack.id,
            module_id=module_spec.module_id,
            row_index=module_spec.row_index,
            start_hp=module_spec.start_hp,
        )
        db.add(db_rack_module)
        module = db.query(Module).filter(Module.id == module_spec.module_id).first()
        if module:
            modules.append(module)

    db.commit()
    db.refresh(db_rack)

    # Build response
    return build_rack_response(db, db_rack)


@router.get("/", response_model=RackListResponse)
def list_racks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_public: Optional[bool] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List racks with optional filters."""
    query = db.query(Rack)

    # Apply filters
    if is_public is not None:
        query = query.filter(Rack.is_public == is_public)
    if user_id is not None:
        query = query.filter(Rack.user_id == user_id)

    total = query.count()
    racks = query.offset(skip).limit(limit).all()

    rack_responses = [build_rack_response(db, rack) for rack in racks]

    return RackListResponse(total=total, racks=rack_responses)


@router.get("/{rack_id}", response_model=RackResponse)
def get_rack(rack_id: int, db: Session = Depends(get_db)):
    """Get a specific rack by ID."""
    rack = db.query(Rack).filter(Rack.id == rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    return build_rack_response(db, rack)


@router.patch("/{rack_id}", response_model=RackResponse)
def update_rack(rack_id: int, rack_update: RackUpdate, db: Session = Depends(get_db)):
    """Update a rack."""
    db_rack = db.query(Rack).filter(Rack.id == rack_id).first()
    if not db_rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    # Update basic fields
    update_data = rack_update.model_dump(exclude_unset=True, exclude={"modules", "name_suggested"})
    for field, value in update_data.items():
        setattr(db_rack, field, value)

    # Update modules if provided
    if rack_update.modules is not None:
        # Validate new configuration
        is_valid, errors = validate_rack_configuration(
            db, db_rack.case_id, rack_update.modules
        )
        if not is_valid:
            raise HTTPException(
                status_code=400, detail={"message": "Rack validation failed", "errors": errors}
            )

        # Delete existing modules
        db.query(RackModule).filter(RackModule.rack_id == rack_id).delete()

        # Add new modules
        modules = []
        for module_spec in rack_update.modules:
            db_rack_module = RackModule(
                rack_id=db_rack.id,
                module_id=module_spec.module_id,
                row_index=module_spec.row_index,
                start_hp=module_spec.start_hp,
            )
            db.add(db_rack_module)
            module = db.query(Module).filter(Module.id == module_spec.module_id).first()
            if module:
                modules.append(module)

        if not db_rack.name_suggested:
            db_rack.name_suggested = generate_rig_suggested_name(modules)

    db.commit()
    db.refresh(db_rack)

    return build_rack_response(db, db_rack)


@router.delete("/{rack_id}", status_code=204)
def delete_rack(rack_id: int, db: Session = Depends(get_db)):
    """Delete a rack."""
    db_rack = db.query(Rack).filter(Rack.id == rack_id).first()
    if not db_rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    db.delete(db_rack)
    db.commit()
    return None


def build_rack_response(db: Session, rack: Rack) -> RackResponse:
    """Build a complete rack response with related data."""
    # Get case
    case = db.query(Case).filter(Case.id == rack.case_id).first()

    # Get modules with details
    rack_modules = db.query(RackModule).filter(RackModule.rack_id == rack.id).all()
    modules_response = []
    for rm in rack_modules:
        module = db.query(Module).filter(Module.id == rm.module_id).first()
        modules_response.append(
            {
                "id": rm.id,
                "module_id": rm.module_id,
                "row_index": rm.row_index,
                "start_hp": rm.start_hp,
                "module": {
                    "id": module.id,
                    "brand": module.brand,
                    "name": module.name,
                    "hp": module.hp,
                    "module_type": module.module_type,
                }
                if module
                else None,
            }
        )

    # Count votes
    from community.models import Vote

    vote_count = db.query(Vote).filter(Vote.rack_id == rack.id).count()

    return RackResponse(
        id=rack.id,
        user_id=rack.user_id,
        case_id=rack.case_id,
        name=rack.name,
        name_suggested=rack.name_suggested,
        description=rack.description,
        tags=rack.tags,
        is_public=rack.is_public,
        generation_seed=rack.generation_seed,
        created_at=rack.created_at,
        updated_at=rack.updated_at,
        modules=modules_response,
        case={
            "id": case.id,
            "brand": case.brand,
            "name": case.name,
            "total_hp": case.total_hp,
            "rows": case.rows,
            "hp_per_row": case.hp_per_row,
        }
        if case
        else None,
        vote_count=vote_count,
    )
