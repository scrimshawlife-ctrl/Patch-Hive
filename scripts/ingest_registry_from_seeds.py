#!/usr/bin/env python3
"""
PDB Phase 2 ingester: Load synth-catalog seeds into registry structures.

- Reads data/synth-catalog/seed-phase2-v1.json (and similar future seeds).
- Builds in-memory Manufacturer / Model structures.
- Produces deterministic registry snapshot + coverage report.
- Pure Python (no DB required for this execution).

Output:
  data/registry_snapshots/registry_<date>.json
  data/registry_snapshots/coverage_<date>.json

Run: python scripts/ingest_registry_from_seeds.py
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
SEED_DIR = ROOT / "data" / "synth-catalog"
SNAPSHOT_DIR = ROOT / "data" / "registry_snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def slugify(name: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_seed(seed_path: Path) -> dict:
    with open(seed_path, encoding="utf-8") as f:
        return json.load(f)


def ingest_phase2(seed: dict) -> dict:
    """Convert Phase 2 seed into registry-shaped data."""
    brands = seed.get("brands", [])
    modules = seed.get("catalog_modules", []) or seed.get("modules", []) or seed.get("catalog", [])  # flexible

    manufacturers = []
    for brand in brands:
        if not brand or not isinstance(brand, str):
            continue
        m_slug = slugify(brand)
        manufacturers.append({
            "canonical_name": brand,
            "slug": m_slug,
            "aliases": [],
            "website": None,
            "status": "active",
            "provenance": {"source": "synth-catalog-phase2"},
            "models": []
        })

    # Attach simple models from any module list in seed
    brand_index: dict[str, dict] = {m["slug"]: m for m in manufacturers}

    for mod in (modules if isinstance(modules, list) else []):
        if not isinstance(mod, dict):
            continue
        brand = mod.get("brand") or mod.get("manufacturer")
        if not brand:
            continue
        bslug = slugify(brand)
        if bslug not in brand_index:
            brand_index[bslug] = {
                "canonical_name": brand,
                "slug": bslug,
                "aliases": [],
                "status": "active",
                "provenance": {"source": "synth-catalog-phase2"},
                "models": []
            }
            manufacturers.append(brand_index[bslug])

        model = {
            "canonical_name": mod.get("name", "Unknown"),
            "slug": slugify(f"{brand}-{mod.get('name', 'unknown')}"),
            "device_type": mod.get("category") or mod.get("type"),
            "format": "eurorack",
            "hp": mod.get("hp"),
            "depth_mm": None,
            "release_state": "available",
            "provenance": {"source": "synth-catalog-phase2"},
            "revisions": []
        }
        brand_index[bslug]["models"].append(model)

    return {"manufacturers": manufacturers}


def compute_coverage(registry: dict) -> dict:
    mans = registry.get("manufacturers", [])
    total_brands = len(mans)
    total_models = 0
    hp_known = 0
    for m in mans:
        for model in m.get("models", []):
            total_models += 1
            if model.get("hp") is not None:
                hp_known += 1

    coverage_pct = round(100.0 * hp_known / total_models, 1) if total_models else 0.0

    return {
        "total_manufacturers": total_brands,
        "total_models": total_models,
        "hp_known": hp_known,
        "hp_unknown": total_models - hp_known,
        "hp_coverage_pct": coverage_pct,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def write_snapshot(data: dict, prefix: str = "registry") -> Path:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M")
    path = SNAPSHOT_DIR / f"{prefix}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    # Also write a stable latest pointer (for convenience)
    latest = SNAPSHOT_DIR / f"{prefix}_latest.json"
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return path


def main() -> int:
    print("=== Registry Ingester (PDB Phase 2) ===")
    seeds = list(SEED_DIR.glob("seed-phase2*.json")) + list(SEED_DIR.glob("*-v1.json"))
    if not seeds:
        print("No Phase 2 seeds found.")
        return 1

    all_manufacturers: list[dict] = []
    for seed_path in seeds[:3]:  # limit for speed in this run
        print(f"Loading {seed_path.name}...")
        seed = load_seed(seed_path)
        ingested = ingest_phase2(seed)
        all_manufacturers.extend(ingested["manufacturers"])

    # Dedup by slug
    seen = {}
    for m in all_manufacturers:
        if m["slug"] not in seen:
            seen[m["slug"]] = m
    deduped = list(seen.values())

    snapshot = {
        "schema_version": "registry-1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_seeds": [s.name for s in seeds[:3]],
        "manufacturers": deduped,
    }

    coverage = compute_coverage(snapshot)

    snap_path = write_snapshot(snapshot, "registry")
    cov_path = write_snapshot(coverage, "coverage")

    # Hash for provenance
    with open(snap_path, "rb") as f:
        snap_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    print(f"Snapshot: {snap_path} (sha256:{snap_hash})")
    print(f"Coverage: {cov_path}")
    print(f"Manufacturers: {coverage['total_manufacturers']}")
    print(f"Models: {coverage['total_models']} (HP known: {coverage['hp_known']}, coverage: {coverage['hp_coverage_pct']}%)")

    # Emit a tiny receipt inline
    receipt = {
        "plan": "CONTINUATION_PLAN_PDB_P0_20260723",
        "phase": "2-ingestion",
        "snapshot": str(snap_path.relative_to(ROOT)),
        "coverage": str(cov_path.relative_to(ROOT)),
        "stats": coverage,
        "hash": snap_hash,
    }
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
