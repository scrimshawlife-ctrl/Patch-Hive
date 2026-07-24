#!/usr/bin/env python3
"""
One-shot DB population for Device Registry from snapshot (PDB Phase 2/3).
Run inside container or with proper DB URL.
"""
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from registry.models import Manufacturer, DeviceModel

def main():
    snap_path = Path("data/registry_snapshots/registry_latest.json")
    if not snap_path.exists():
        print("Snapshot not found")
        return
    data = json.loads(snap_path.read_text())
    mans = data.get("manufacturers", [])
    db: Session = SessionLocal()
    m_count = 0
    mod_count = 0
    for m in mans:
        slug = m.get("slug")
        if not slug: continue
        man = db.query(Manufacturer).filter_by(slug=slug).first()
        if not man:
            man = Manufacturer(
                canonical_name=m.get("name") or m.get("canonical_name") or slug,
                slug=slug,
                aliases=m.get("aliases", []),
                website=m.get("website"),
                status="active",
                provenance={"source": "synth-catalog"},
                created_at=datetime.utcnow(),
            )
            db.add(man)
            m_count += 1
        for mod in m.get("models", []):
            mslug = mod.get("slug")
            if not mslug: continue
            if not db.query(DeviceModel).filter_by(slug=mslug).first():
                db.add(DeviceModel(
                    manufacturer_id=man.id,
                    canonical_name=mod.get("canonical_name") or mod.get("name") or mslug,
                    slug=mslug,
                    hp=mod.get("hp"),
                    device_type=mod.get("device_type"),
                    provenance={"source": "synth-catalog"},
                ))
                mod_count += 1
    db.commit()
    db.close()
    print(f"Inserted {m_count} manufacturers, {mod_count} models")

if __name__ == "__main__":
    main()
