"""
FastAPI routes for Patch management and generation.
"""
from typing import Optional, Any
from dataclasses import asdict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core import get_db, settings
from racks.models import Rack
from runs.models import Run
from .models import Patch
from .schemas import (
    PatchCreate,
    PatchUpdate,
    PatchResponse,
    PatchListResponse,
    GeneratePatchesRequest,
    GeneratePatchesResponse,
)
from .engine import generate_patches_with_ir, PatchEngineConfig
from runs.models import Run

router = APIRouter()


@router.post("/", response_model=PatchResponse, status_code=201)
def create_patch(patch: PatchCreate, db: Session = Depends(get_db)):
    """Create a new patch."""
    # Verify rack exists
    rack = db.query(Rack).filter(Rack.id == patch.rack_id).first()
    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    tags = patch.tags or _derive_tags(patch.connections)
    db_patch = Patch(
        rack_id=patch.rack_id,
        run_id=None,
    return build_patch_response(db, db_patch)


@router.get("/", response_model=PatchListResponse)
def list_patches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rack_id: Optional[int] = None,
    run_id: Optional[int] = None,
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List patches with optional filters."""
    query = db.query(Patch)

    # Apply filters
    if rack_id is not None:
        query = query.filter(Patch.rack_id == rack_id)
    if run_id is not None:
        query = query.filter(Patch.run_id == run_id)
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

    if "name_override" in update_data:
        if patch_update.name_override:
            db_patch.name = patch_update.name_override
        else:
            db_patch.name = db_patch.suggested_name or db_patch.name

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

    # Create run
    run = Run(rack_id=rack_id, status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)
    generation_ir, patch_graphs, provenance = generate_patches_with_ir(
        db, rack, seed=request.seed, config=config
    )

    # Save patches to database
    saved_patches = []
    for spec in patch_graphs:
        tags = _derive_tags([c.to_dict() for c in spec.connections])
        db_patch = Patch(
            rack_id=rack_id,
            run_id=run.id,
            name=spec.patch_name,
    new_run.status = "completed"
    db.commit()

    # Build responses
    patch_responses = [build_patch_response(db, p) for p in saved_patches]

    return GeneratePatchesResponse(
        generated_count=len(patch_responses), patches=patch_responses, run_id=run.id

def build_patch_response(db: Session, patch: Patch) -> PatchResponse:
    """Build a complete patch response with vote count."""
    from community.models import Vote

    vote_count = db.query(Vote).filter(Vote.patch_id == patch.id).count()

    return PatchResponse(
        id=patch.id,
        rack_id=patch.rack_id,
        run_id=patch.run_id,
        name=patch.name,
        suggested_name=patch.suggested_name,
        name_override=patch.name_override,
        category=patch.category,
        description=patch.description,
        connections=patch.connections,
        generation_seed=patch.generation_seed,
        generation_version=patch.generation_version,
        engine_config=patch.engine_config,
        waveform_svg_path=patch.waveform_svg_path,
        waveform_params=patch.waveform_params,
        is_public=patch.is_public,
        tags=patch.tags or [],
        suggested_name=patch.name,
        difficulty=_derive_difficulty(patch.connections),
        diagram_svg_url=f"/api/export/patches/{patch.id}/diagram.svg",
        created_at=patch.created_at,
        updated_at=patch.updated_at,
        vote_count=vote_count,
    )


def _derive_difficulty(connections: list[dict[str, Any]]) -> str:
    connection_count = len(connections)
    has_feedback = any(c.get("from_module_id") == c.get("to_module_id") for c in connections)
    if connection_count <= 2 and not has_feedback:
        return "Easy"
    if connection_count <= 4 and not has_feedback:
        return "Medium"
    return "Hard"


def _derive_tags(connections: list[dict[str, Any]]) -> list[str]:
    tags: list[str] = []
    if any(c.get("from_module_id") == c.get("to_module_id") for c in connections):
        tags.append("humor")
    return tags
