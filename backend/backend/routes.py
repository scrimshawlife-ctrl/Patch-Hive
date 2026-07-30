"""
Registry API routes (PDB-03 stubs).

Mount under /registry or /products later.
These are read-only for the public Product Database / Explorer.

Example mounting (in main.py later):
    from registry.routes import router as registry_router
    app.include_router(registry_router, prefix="/registry", tags=["registry"])
"""

from typing import Optional

from fastapi import APIRouter, Query

from . import services

router = APIRouter()


@router.get("/manufacturers")
def list_manufacturers(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
):
    return {
        "total": len(services.list_manufacturers(limit=10000)),
        "items": services.list_manufacturers(limit=limit, offset=offset),
    }


@router.get("/manufacturers/{slug}")
def get_manufacturer(slug: str):
    detail = services.get_manufacturer_detail(slug)
    if detail:
        return detail
    m = services.get_manufacturer(slug)
    if not m:
        from fastapi import HTTPException
        raise HTTPException(404, "Manufacturer not found")
    return m


@router.get("/search")
def search(
    q: str = Query("", description="Search term"),
    brand: Optional[str] = None,
    limit: int = Query(50, le=200),
):
    return {"results": services.search_models(q=q, brand=brand, limit=limit)}


@router.get("/coverage")
def coverage():
    return services.get_coverage_report()


# --- Basic admin curation endpoints (Phase 2/3) ---
from fastapi import HTTPException
from pydantic import BaseModel

class ManufacturerCreate(BaseModel):
    slug: str
    canonical_name: str
    website: str | None = None
    aliases: list[str] = []

@router.post("/admin/manufacturers", tags=["admin", "registry"])
def create_manufacturer(payload: ManufacturerCreate):
    # In real use, protect with admin dependency
    from core.database import SessionLocal
    from registry.models import Manufacturer
    db = SessionLocal()
    if db.query(Manufacturer).filter_by(slug=payload.slug).first():
        db.close()
        raise HTTPException(400, "Slug already exists")
    m = Manufacturer(
        slug=payload.slug,
        canonical_name=payload.canonical_name,
        website=payload.website,
        aliases=payload.aliases,
        status="active",
        provenance={"source": "admin-curation"},
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    db.close()
    return {"id": m.id, "slug": m.slug}


@router.get("/manufacturers/{slug}/models")
def models_for_manufacturer(slug: str, limit: int = 50):
    return {"models": services.list_models_for_manufacturer(slug, limit=limit)}
