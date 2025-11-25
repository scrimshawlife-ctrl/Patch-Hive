"""
FastAPI routes for Patch management and generation.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db, settings
from racks.models import Rack
from .models import Patch
from .schemas import (
    PatchCreate,
    PatchUpdate,
    PatchResponse,
    PatchListResponse,
    GeneratePatchesRequest,
    GeneratePatchesResponse,
)
from .engine import generate_patches_for_rack, PatchEngineConfig

router = APIRouter()


@router.post("/", response_model=PatchResponse, status_code=201)
def create_patch(patch: PatchCreate, db: Session = Depends(get_db)):
    """Create a new patch."""
    # Verify rack exists
    rack = db.query(Rack).filter(Rack.id == patch.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    db_patch = Patch(
        rack_id=patch.rack_id,
        name=patch.name,
        category=patch.category,
        description=patch.description,
        connections=patch.connections,
        generation_seed=patch.generation_seed,
        generation_version=patch.generation_version,
        engine_config=patch.engine_config,
        waveform_params=patch.waveform_params,
        is_public=patch.is_public,
    )
    db.add(db_patch)
    db.commit()
    db.refresh(db_patch)

    return build_patch_response(db, db_patch)


@router.get("/", response_model=PatchListResponse)
def list_patches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rack_id: Optional[int] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List patches with optional filters."""
    query = db.query(Patch)

    # Apply filters
    if rack_id is not None:
        query = query.filter(Patch.rack_id == rack_id)
    if category is not None:
        query = query.filter(Patch.category == category)
    if is_public is not None:
        query = query.filter(Patch.is_public == is_public)

    total = query.count()
    patches = query.offset(skip).limit(limit).all()

    patch_responses = [build_patch_response(db, p) for p in patches]

    return PatchListResponse(total=total, patches=patch_responses)


@router.get("/{patch_id}", response_model=PatchResponse)
def get_patch(patch_id: int, db: Session = Depends(get_db)):
    """Get a specific patch by ID."""
    patch = db.query(Patch).filter(Patch.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")

    return build_patch_response(db, patch)


@router.patch("/{patch_id}", response_model=PatchResponse)
def update_patch(patch_id: int, patch_update: PatchUpdate, db: Session = Depends(get_db)):
    """Update a patch."""
    db_patch = db.query(Patch).filter(Patch.id == patch_id).first()
    if not db_patch:
        raise HTTPException(status_code=404, detail="Patch not found")

    # Update fields if provided
    update_data = patch_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patch, field, value)

    db.commit()
    db.refresh(db_patch)

    return build_patch_response(db, db_patch)


@router.delete("/{patch_id}", status_code=204)
def delete_patch(patch_id: int, db: Session = Depends(get_db)):
    """Delete a patch."""
    db_patch = db.query(Patch).filter(Patch.id == patch_id).first()
    if not db_patch:
        raise HTTPException(status_code=404, detail="Patch not found")

    db.delete(db_patch)
    db.commit()
    return None


@router.post("/generate/{rack_id}", response_model=GeneratePatchesResponse)
def generate_patches(
    rack_id: int, request: GeneratePatchesRequest, db: Session = Depends(get_db)
):
    """Generate patches for a rack using the patch engine."""
    # Verify rack exists
    rack = db.query(Rack).filter(Rack.id == rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    # Build engine config
    config = PatchEngineConfig(
        max_patches=request.max_patches or settings.max_patches_per_generation,
        allow_feedback=request.allow_feedback,
        prefer_simple=request.prefer_simple,
    )

    # Generate patches
    patch_specs = generate_patches_for_rack(db, rack, seed=request.seed, config=config)

    # Save patches to database
    saved_patches = []
    for spec in patch_specs:
        db_patch = Patch(
            rack_id=rack_id,
            name=spec.name,
            category=spec.category,
            description=spec.description,
            connections=[c.to_dict() for c in spec.connections],
            generation_seed=spec.generation_seed,
            generation_version=settings.patch_engine_version,
            engine_config={
                "max_patches": config.max_patches,
                "allow_feedback": config.allow_feedback,
                "prefer_simple": config.prefer_simple,
            },
            is_public=False,
        )
        db.add(db_patch)
        saved_patches.append(db_patch)

    db.commit()

    # Build responses
    patch_responses = [build_patch_response(db, p) for p in saved_patches]

    return GeneratePatchesResponse(
        generated_count=len(patch_responses), patches=patch_responses
    )


def build_patch_response(db: Session, patch: Patch) -> PatchResponse:
    """Build a complete patch response with vote count."""
    from community.models import Vote

    vote_count = db.query(Vote).filter(Vote.patch_id == patch.id).count()

    return PatchResponse(
        id=patch.id,
        rack_id=patch.rack_id,
        name=patch.name,
        category=patch.category,
        description=patch.description,
        connections=patch.connections,
        generation_seed=patch.generation_seed,
        generation_version=patch.generation_version,
        engine_config=patch.engine_config,
        waveform_svg_path=patch.waveform_svg_path,
        waveform_params=patch.waveform_params,
        is_public=patch.is_public,
        created_at=patch.created_at,
        updated_at=patch.updated_at,
        vote_count=vote_count,
    )
