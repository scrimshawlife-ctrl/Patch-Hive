"""
Module Catalog API endpoints - browse/search/filter modules.

Fast, lightweight catalog of all available modules.
Full specs fetched on-demand when user adds to rack.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional

from core.database import get_db
from modules.catalog import ModuleCatalog

router = APIRouter()


@router.get("/catalog")
def browse_module_catalog(
    db: Session = Depends(get_db),
    # Search
    search: Optional[str] = Query(None, description="Search in brand/name"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    category: Optional[str] = Query(None, description="Filter by category (VCO, VCF, etc.)"),
    # Size filters
    hp_min: Optional[int] = Query(None, description="Minimum HP width"),
    hp_max: Optional[int] = Query(None, description="Maximum HP width"),
    # Status
    is_available: Optional[str] = Query(None, description="available, discontinued, upcoming"),
    # Pagination
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    # Sorting
    sort_by: str = Query("brand", regex="^(brand|name|hp|category|created_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
):
    """
    Browse module catalog with search, filters, and sorting.

    This is a lightweight endpoint for browsing thousands of modules.
    Returns basic info only. Fetch full specs separately when needed.

    Examples:
        - /catalog?search=maths
        - /catalog?brand=Mutable+Instruments&category=VCO
        - /catalog?hp_min=8&hp_max=16
        - /catalog?sort_by=hp&sort_order=asc
    """
    query = db.query(ModuleCatalog)

    # Apply filters
    filters = []

    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                ModuleCatalog.brand.ilike(search_term),
                ModuleCatalog.name.ilike(search_term)
            )
        )

    if brand:
        filters.append(ModuleCatalog.brand == brand)

    if category:
        filters.append(ModuleCatalog.category == category)

    if hp_min is not None:
        filters.append(ModuleCatalog.hp >= hp_min)

    if hp_max is not None:
        filters.append(ModuleCatalog.hp <= hp_max)

    if is_available:
        filters.append(ModuleCatalog.is_available == is_available)

    if filters:
        query = query.filter(and_(*filters))

    # Count total matches
    total = query.count()

    # Apply sorting
    sort_column = getattr(ModuleCatalog, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    modules = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "modules": [m.to_dict() for m in modules]
    }


@router.get("/catalog/brands")
def list_catalog_brands(db: Session = Depends(get_db)):
    """Get list of all brands in catalog with module counts."""
    from sqlalchemy import func

    brands = db.query(
        ModuleCatalog.brand,
        func.count(ModuleCatalog.id).label('count')
    ).group_by(ModuleCatalog.brand).order_by(ModuleCatalog.brand).all()

    return {
        "total": len(brands),
        "brands": [{"name": brand, "module_count": count} for brand, count in brands]
    }


@router.get("/catalog/categories")
def list_catalog_categories(db: Session = Depends(get_db)):
    """Get list of all categories with module counts."""
    from sqlalchemy import func

    categories = db.query(
        ModuleCatalog.category,
        func.count(ModuleCatalog.id).label('count')
    ).group_by(ModuleCatalog.category).order_by(
        func.count(ModuleCatalog.id).desc()
    ).all()

    return {
        "total": len(categories),
        "categories": [{"name": cat, "module_count": count} for cat, count in categories if cat]
    }


@router.get("/catalog/stats")
def get_catalog_stats(db: Session = Depends(get_db)):
    """Get catalog statistics."""
    from sqlalchemy import func

    total_modules = db.query(func.count(ModuleCatalog.id)).scalar()
    total_brands = db.query(func.count(func.distinct(ModuleCatalog.brand))).scalar()
    total_categories = db.query(func.count(func.distinct(ModuleCatalog.category))).scalar()

    # HP distribution
    avg_hp = db.query(func.avg(ModuleCatalog.hp)).scalar()
    min_hp = db.query(func.min(ModuleCatalog.hp)).scalar()
    max_hp = db.query(func.max(ModuleCatalog.hp)).scalar()

    # Availability
    available_count = db.query(func.count(ModuleCatalog.id)).filter(
        ModuleCatalog.is_available == "available"
    ).scalar()

    return {
        "total_modules": total_modules or 0,
        "total_brands": total_brands or 0,
        "total_categories": total_categories or 0,
        "hp_stats": {
            "average": round(float(avg_hp or 0), 1),
            "min": min_hp or 0,
            "max": max_hp or 0,
        },
        "availability": {
            "available": available_count or 0,
            "discontinued": total_modules - (available_count or 0) if total_modules else 0,
        }
    }


@router.get("/catalog/{slug}")
def get_catalog_module(slug: str, db: Session = Depends(get_db)):
    """
    Get catalog entry for specific module.

    Returns lightweight catalog info. Use /modules/{id} for full specs.
    """
    module = db.query(ModuleCatalog).filter(ModuleCatalog.slug == slug).first()

    if not module:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Module '{slug}' not found in catalog")

    return module.to_dict()
