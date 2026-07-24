"""
Registry services — query layer for Product Database.

Provides pure functions over the registry snapshot or (later) DB session.
Designed to be fast and deterministic for catalog/explorer use.
"""

from typing import Optional
import json
from pathlib import Path

SNAPSHOT_LATEST = Path(__file__).parent.parent.parent / "data" / "registry_snapshots" / "registry_latest.json"


def load_latest_snapshot() -> dict:
    if SNAPSHOT_LATEST.exists():
        return json.loads(SNAPSHOT_LATEST.read_text())
    return {"manufacturers": []}


def list_manufacturers(limit: int = 100, offset: int = 0, db: "Session | None" = None) -> list[dict]:
    # DB primary (enriched)
    try:
        from sqlalchemy.orm import Session
        from core.database import SessionLocal
        from registry.models import Manufacturer
        if db is None:
            db = SessionLocal()
        rows = db.query(Manufacturer).order_by(Manufacturer.canonical_name).offset(offset).limit(limit).all()
        return [
            {
                "id": r.id,
                "slug": r.slug,
                "name": r.canonical_name,
                "model_count": 0,
                "status": r.status or "active",
            }
            for r in rows
        ]
    except Exception:
        # fallback
        snap = load_latest_snapshot()
        mans = snap.get("manufacturers", [])[offset:offset + limit]
        return [
            {
                "slug": m.get("slug"),
                "name": m.get("canonical_name"),
                "model_count": len(m.get("models", [])),
                "status": m.get("status"),
            }
            for m in mans
        ]


def get_manufacturer(slug: str) -> Optional[dict]:
    snap = load_latest_snapshot()
    for m in snap.get("manufacturers", []):
        if m.get("slug") == slug:
            return m
    return None


def search_models(q: str = "", brand: Optional[str] = None, limit: int = 50) -> list[dict]:
    snap = load_latest_snapshot()
    q = q.lower()
    results = []
    for m in snap.get("manufacturers", []):
        if brand and m.get("slug") != brand and m.get("canonical_name", "").lower() != brand.lower():
            continue
        for model in m.get("models", []):
            name = model.get("canonical_name", "")
            if not q or q in name.lower() or q in m.get("canonical_name", "").lower():
                results.append({
                    "brand": m.get("canonical_name"),
                    "name": name,
                    "slug": model.get("slug"),
                    "hp": model.get("hp"),
                    "device_type": model.get("device_type"),
                })
                if len(results) >= limit:
                    return results
    return results



# --- DB-backed versions (Phase 2 continuation) ---
from sqlalchemy.orm import Session
from core.database import SessionLocal
from registry.models import Manufacturer, DeviceModel

def _get_db() -> Session:
    return SessionLocal()

def list_manufacturers(limit: int = 100, offset: int = 0, db: Session | None = None) -> list[dict]:
    if db is None:
        db = _get_db()
    rows = (
        db.query(Manufacturer)
        .order_by(Manufacturer.canonical_name)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "slug": r.slug,
            "name": r.canonical_name,
            "model_count": 0,  # could count later
            "status": r.status or "active",
        }
        for r in rows
    ]

def get_coverage_report(db: Session | None = None) -> dict:
    if db is None:
        db = _get_db()
    total_mans = db.query(Manufacturer).count()
    total_models = db.query(DeviceModel).count()
    return {
        "total_manufacturers": total_mans,
        "total_models": total_models,
        "hp_coverage_pct": 0,  # TODO: compute from models
    }


def list_models_for_manufacturer(manufacturer_slug: str, limit: int = 50) -> list[dict]:
    db = _get_db()
    man = db.query(Manufacturer).filter_by(slug=manufacturer_slug).first()
    if not man:
        return []
    models = db.query(DeviceModel).filter_by(manufacturer_id=man.id).limit(limit).all()
    return [
        {
            "id": m.id,
            "slug": m.slug,
            "name": m.canonical_name,
            "hp": m.hp,
            "device_type": m.device_type,
            "format": m.format,
        }
        for m in models
    ]

def get_manufacturer_detail(slug: str) -> Optional[dict]:
    db = _get_db()
    man = db.query(Manufacturer).filter_by(slug=slug).first()
    if not man:
        return None
    models = list_models_for_manufacturer(slug, limit=100)
    return {
        "id": man.id,
        "slug": man.slug,
        "name": man.canonical_name,
        "website": man.website,
        "status": man.status,
        "model_count": len(models),
        "models": models,
    }
