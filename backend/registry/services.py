"""Registry query services for the Product Database explorer.

HTTP callers provide a database session. Direct callers without a session use the
versioned registry snapshot, which keeps scripts and tests deterministic and avoids
opening an implicit production connection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from registry.models import DeviceModel, Manufacturer

SNAPSHOT_LATEST = (
    Path(__file__).parent.parent.parent
    / "data"
    / "registry_snapshots"
    / "registry_latest.json"
)


def load_latest_snapshot() -> dict:
    if SNAPSHOT_LATEST.exists():
        return json.loads(SNAPSHOT_LATEST.read_text())
    return {"manufacturers": []}


def _snapshot_manufacturers() -> list[dict]:
    return load_latest_snapshot().get("manufacturers", [])


def _manufacturer_summary(manufacturer: dict) -> dict:
    return {
        "slug": manufacturer.get("slug"),
        "name": manufacturer.get("canonical_name"),
        "model_count": len(manufacturer.get("models", [])),
        "status": manufacturer.get("status"),
    }


def list_manufacturers(
    limit: int = 100,
    offset: int = 0,
    db: Session | None = None,
) -> list[dict]:
    if db is None:
        return [
            _manufacturer_summary(manufacturer)
            for manufacturer in _snapshot_manufacturers()[offset : offset + limit]
        ]

    rows = (
        db.query(Manufacturer)
        .order_by(Manufacturer.canonical_name)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": row.id,
            "slug": row.slug,
            "name": row.canonical_name,
            "model_count": db.query(DeviceModel)
            .filter(DeviceModel.manufacturer_id == row.id)
            .count(),
            "status": row.status or "active",
        }
        for row in rows
    ]


def get_manufacturer(slug: str) -> Optional[dict]:
    for manufacturer in _snapshot_manufacturers():
        if manufacturer.get("slug") == slug:
            return manufacturer
    return None


def search_models(q: str = "", brand: Optional[str] = None, limit: int = 50) -> list[dict]:
    query = q.lower()
    results = []
    for manufacturer in _snapshot_manufacturers():
        if (
            brand
            and manufacturer.get("slug") != brand
            and manufacturer.get("canonical_name", "").lower() != brand.lower()
        ):
            continue
        for model in manufacturer.get("models", []):
            name = model.get("canonical_name", "")
            if not query or query in name.lower() or query in manufacturer.get(
                "canonical_name", ""
            ).lower():
                results.append(
                    {
                        "brand": manufacturer.get("canonical_name"),
                        "name": name,
                        "slug": model.get("slug"),
                        "hp": model.get("hp"),
                        "device_type": model.get("device_type"),
                    }
                )
                if len(results) >= limit:
                    return results
    return results


def get_coverage_report(db: Session | None = None) -> dict:
    if db is not None:
        total_manufacturers = db.query(Manufacturer).count()
        total_models = db.query(DeviceModel).count()
        models_with_hp = db.query(DeviceModel).filter(DeviceModel.hp.is_not(None)).count()
    else:
        manufacturers = _snapshot_manufacturers()
        models = [model for manufacturer in manufacturers for model in manufacturer.get("models", [])]
        total_manufacturers = len(manufacturers)
        total_models = len(models)
        models_with_hp = sum(model.get("hp") is not None for model in models)

    hp_coverage_pct = round((models_with_hp / total_models) * 100, 2) if total_models else 0
    return {
        "total_manufacturers": total_manufacturers,
        "total_models": total_models,
        "hp_coverage_pct": hp_coverage_pct,
    }


def list_models_for_manufacturer(
    manufacturer_slug: str,
    limit: int = 50,
    db: Session | None = None,
) -> list[dict]:
    if db is None:
        manufacturer = get_manufacturer(manufacturer_slug)
        if not manufacturer:
            return []
        return [
            {
                "slug": model.get("slug"),
                "name": model.get("canonical_name"),
                "hp": model.get("hp"),
                "device_type": model.get("device_type"),
                "format": model.get("format"),
            }
            for model in manufacturer.get("models", [])[:limit]
        ]

    manufacturer = db.query(Manufacturer).filter_by(slug=manufacturer_slug).first()
    if not manufacturer:
        return []
    models = (
        db.query(DeviceModel)
        .filter_by(manufacturer_id=manufacturer.id)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": model.id,
            "slug": model.slug,
            "name": model.canonical_name,
            "hp": model.hp,
            "device_type": model.device_type,
            "format": model.format,
        }
        for model in models
    ]


def get_manufacturer_detail(slug: str, db: Session | None = None) -> Optional[dict]:
    if db is None:
        manufacturer = get_manufacturer(slug)
        if not manufacturer:
            return None
        models = list_models_for_manufacturer(slug, limit=100)
        return {
            "slug": manufacturer.get("slug"),
            "name": manufacturer.get("canonical_name"),
            "website": manufacturer.get("website"),
            "status": manufacturer.get("status"),
            "model_count": len(models),
            "models": models,
        }

    manufacturer = db.query(Manufacturer).filter_by(slug=slug).first()
    if not manufacturer:
        return None
    models = list_models_for_manufacturer(slug, limit=100, db=db)
    return {
        "id": manufacturer.id,
        "slug": manufacturer.slug,
        "name": manufacturer.canonical_name,
        "website": manufacturer.website,
        "status": manufacturer.status,
        "model_count": len(models),
        "models": models,
    }
