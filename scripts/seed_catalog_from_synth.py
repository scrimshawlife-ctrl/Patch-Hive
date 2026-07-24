#!/usr/bin/env python3
"""
Seed ModuleCatalog from synth-catalog seed-phase2-v1.json.

- Populates lightweight catalog rows (for fast browsing).
- Wires registry_manufacturer_slug and registry_device_slug by matching to Device Registry.
- Idempotent (upserts on slug).
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from modules.catalog import ModuleCatalog
from registry.models import Manufacturer, DeviceModel

def create_slug(brand: str, name: str) -> str:
    import re
    combined = f"{brand}-{name}".lower()
    slug = re.sub(r"[^a-z0-9]+", "-", combined).strip("-")
    return slug or "unknown"

def main(seed_path: str = "/app/data/synth-catalog/seed-phase2-v1.json"):
    seed = Path(seed_path)
    if not seed.exists():
        print(f"Seed not found: {seed}")
        sys.exit(1)

    data = json.loads(seed.read_text())
    modules = data.get("catalog_modules") or data.get("modules") or []
    print(f"Loaded {len(modules)} catalog modules from seed")

    db: Session = SessionLocal()

    # Build quick lookup for registry
    mans_by_name = {}
    for m in db.query(Manufacturer).all():
        mans_by_name[m.canonical_name.lower()] = m.slug
        mans_by_name[m.slug.lower()] = m.slug

    mods_by_brand_name = {}
    for dm in db.query(DeviceModel).all():
        key = (dm.manufacturer.canonical_name.lower() if dm.manufacturer else "", dm.canonical_name.lower())
        mods_by_brand_name[key] = dm.slug

    inserted = 0
    updated = 0

    for m in modules:
        brand = m.get("brand") or m.get("manufacturer") or "Unknown"
        name = m.get("name") or "Unknown Module"
        slug = m.get("slug") or create_slug(brand, name)
        hp = m.get("hp")
        category = m.get("category") or m.get("category_raw")

        existing = db.query(ModuleCatalog).filter_by(slug=slug).first()

        reg_man_slug = None
        brand_lower = brand.lower()
        if brand_lower in mans_by_name:
            reg_man_slug = mans_by_name[brand_lower]
        else:
            # loose match
            for k, v in mans_by_name.items():
                if brand_lower in k or k in brand_lower:
                    reg_man_slug = v
                    break

        reg_dev_slug = None
        if reg_man_slug:
            key = (brand.lower(), name.lower())
            if key in mods_by_brand_name:
                reg_dev_slug = mods_by_brand_name[key]
            else:
                for (b, n), s in list(mods_by_brand_name.items())[:500]:
                    if brand.lower() in b or b in brand.lower():
                        if name.lower()[:12] in n or n[:12] in name.lower():
                            reg_dev_slug = s
                            break

        if existing:
            existing.brand = brand
            existing.name = name
            existing.hp = hp
            existing.category = category
            existing.is_available = m.get("is_available", "available")
            existing.source = m.get("source", "SynthCatalogResearch")
            existing.registry_manufacturer_slug = reg_man_slug
            existing.registry_device_slug = reg_dev_slug
            existing.updated_at = datetime.utcnow().isoformat()
            updated += 1
        else:
            row = ModuleCatalog(
                slug=slug,
                brand=brand,
                name=name,
                hp=hp,
                category=category,
                is_available=m.get("is_available", "available"),
                source=m.get("source", "SynthCatalogResearch"),
                manufacturer_url=m.get("manufacturer_url"),
                description=m.get("description"),
                registry_manufacturer_slug=reg_man_slug,
                registry_device_slug=reg_dev_slug,
            )
            db.add(row)
            inserted += 1

        if (inserted + updated) % 50 == 0:
            db.commit()

    db.commit()
    db.close()

    print(f"Inserted: {inserted}, Updated: {updated}")
    print("ModuleCatalog seeded with registry links.")

if __name__ == "__main__":
    main()
