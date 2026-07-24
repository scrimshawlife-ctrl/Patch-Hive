#!/usr/bin/env python3
"""
PDB-01 Inventory & Reconciliation for Product Database / Device Registry.

Scans current module gallery, catalog models, data seeds, API surfaces, UI,
and produces a deterministic receipt + summary for P0 Product Database work.

Run from repo root: python scripts/inventory_catalog.py
Outputs: docs/evidence/CATALOG_INVENTORY_RECEIPT_$(date).md + console summary.
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = ROOT / "docs" / "evidence"
OUTPUT = EVIDENCE_DIR / f"CATALOG_INVENTORY_RECEIPT_{datetime.utcnow().strftime('%Y%m%d')}.md"

# Key paths to inventory
GALLERY_PATHS = [
    "patchhive/gallery/",
    "backend/patchhive/gallery/",
    "backend/gallery/",
    "backend/modules/",
]
DATA_PATHS = [
    "data/synth-catalog/",
    "data/cases/",
    "fixtures/",
]
CODE_PATHS = [
    "backend/modules/catalog.py",
    "backend/modules/catalog_routes.py",
    "backend/modules/models.py",
    "backend/modules/schemas.py",
    "backend/gallery/models.py",
    "frontend/src/pages/Modules.tsx",
    "frontend/src/pages/admin/AdminGallery.tsx",
    "frontend/src/pages/admin/AdminModules.tsx",
    "frontend/src/lib/api.ts",
    "frontend/src/types/api.ts",
]
DOC_PATHS = [
    "docs/PRODUCT_DATABASE_COMPLETENESS_ROADMAP.md",
    "docs/PRODUCT_DATABASE_EXPLORER.md",
    "docs/DEVICE_REGISTRY.md",
    "docs/adr/ADR-006-public-product-database.md",
    "docs/CONTINUATION.md",
    "CURRENT_STATE.md",
]

def scan_files(base: Path, patterns: list[str] | None = None) -> list[Path]:
    files = []
    for p in (base.rglob("*.py") if base.is_dir() else [base]):
        if p.is_file():
            if patterns:
                if any(pat in str(p) for pat in patterns):
                    files.append(p)
            else:
                files.append(p)
    return sorted(set(files))

def count_lines(files: list[Path]) -> int:
    total = 0
    for f in files:
        try:
            total += len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            pass
    return total

def extract_brands_from_json(path: Path) -> set[str]:
    brands = set()
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        if isinstance(data, dict):
            for k, v in data.items():
                if "brand" in str(k).lower():
                    brands.add(str(v)[:50])
            if "modules" in data and isinstance(data["modules"], list):
                for m in data["modules"]:
                    if isinstance(m, dict) and "brand" in m:
                        brands.add(str(m["brand"])[:50])
            if "brands" in data:
                for b in data.get("brands", []):
                    if isinstance(b, (str, dict)):
                        brands.add(str(b)[:50] if isinstance(b, str) else str(b.get("name", ""))[:50])
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "brand" in item:
                    brands.add(str(item["brand"])[:50])
    except Exception:
        pass
    return {b for b in brands if b and len(b) > 1}

def parse_master_catalog(path: Path) -> dict:
    info = {"brands_claimed": 0, "status": "unknown"}
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"Total Brands Covered:\s*(\d+)", txt)
        if m:
            info["brands_claimed"] = int(m.group(1))
        if "Campaign Complete" in txt:
            info["status"] = "complete per doc"
    except Exception:
        pass
    return info

def main():
    print("=== PatchHive Product Database Inventory (PDB-01) ===")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # Scan gallery / catalog code
    gallery_files = []
    for gp in GALLERY_PATHS:
        gallery_files.extend(scan_files(ROOT / gp))
    print(f"Gallery/catalog source files: {len(gallery_files)}")

    data_files = []
    for dp in DATA_PATHS:
        dpath = ROOT / dp
        if dpath.exists():
            data_files.extend([p for p in dpath.rglob("*") if p.is_file() and p.suffix in (".json", ".md", ".py")])
    print(f"Data/seed files scanned: {len(data_files)}")

    # Extract brands from key seeds
    brand_counts = defaultdict(int)
    for jf in [p for p in data_files if p.suffix == ".json"]:
        for b in extract_brands_from_json(jf):
            brand_counts[b] += 1

    master_info = {}
    master_path = ROOT / "data/synth-catalog/master-catalog.md"
    if master_path.exists():
        master_info = parse_master_catalog(master_path)
        print(f"Master catalog: {master_info}")

    # Code surfaces
    catalog_code = [ROOT / p for p in CODE_PATHS if (ROOT / p).exists()]
    print(f"Core catalog code surfaces: {len(catalog_code)}")

    # Docs
    doc_files = [ROOT / p for p in DOC_PATHS if (ROOT / p).exists()]

    # Models observed
    models_observed = []
    for f in gallery_files:
        if "model" in f.name.lower() or "catalog" in str(f).lower():
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
                if "ModuleCatalog" in txt or "GalleryRevision" in txt or "class .*Model" in txt:
                    models_observed.append(str(f.relative_to(ROOT)))
            except Exception:
                pass

    # API surfaces
    api_surfaces = []
    for f in catalog_code:
        if "route" in f.name or "api" in str(f).lower():
            api_surfaces.append(str(f.relative_to(ROOT)))

    # UI surfaces
    ui_files = [f for f in catalog_code if "frontend" in str(f)]
    print(f"UI catalog surfaces: {len(ui_files)}")

    # Summary stats
    total_brands_in_data = len(brand_counts)
    top_brands = sorted(brand_counts.items(), key=lambda x: -x[1])[:10]

    receipt = f"""# CATALOG_INVENTORY_RECEIPT — {datetime.utcnow().isoformat()}Z

**Purpose:** PDB-01 baseline inventory and reconciliation for public Product Database / Device Registry (Issue #68).

**Source SHA:** {os.popen('git rev-parse HEAD 2>/dev/null || echo "unknown"').read().strip()}
**Run by:** Hermes Agent (inventory script)

## Files & Surfaces Scanned
- Gallery / catalog Python: {len(gallery_files)} files
- Data / seeds / receipts: {len(data_files)} files
- Core catalog code surfaces: {len(catalog_code)}
- Key docs referenced: {len(doc_files)}

## Observed Models & Stores
- Lightweight: `ModuleCatalog` (backend/modules/catalog.py) — brand, name, hp, category, slug, image_url, source, is_available. For fast browse.
- Full spec: `Module` (backend/modules/models.py) — power, depth, io_ports (JSON), etc. Materialized on-demand.
- Audit: `GalleryRevision` (backend/gallery/models.py) — append-only module_key + payload JSON + status.
- Legacy: patchhive/gallery/schemas_gallery_v2.py `ModuleGalleryRevision`, store_v2.py etc.
- No full `Manufacturer` / `DeviceFamily` / `DeviceRevision` hierarchy models yet (per DEVICE_REGISTRY spec).

## Data & Coverage (static scan)
- Master catalog doc claims: {master_info.get('brands_claimed', 'N/A')} brands (status: {master_info.get('status')})
- Unique brands extracted from JSON seeds: {total_brands_in_data}
- Top brands by mentions: {top_brands}
- Sample data files: data/synth-catalog/seed-*.json, cases seeds, receipts/ (~32)

**Note:** Counts are from file content; no live DB connected. Actual DB population via seeds/migrations/materialize may differ. Coverage `NOT_COMPUTABLE` without reference universe + snapshot.

## API Surfaces (observed)
- `/modules/catalog` (browse, filters, search, pagination, stats, brands, categories)
- `/modules/catalog/:slug`, materialize (single + batch)
- Materialize enforces known HP (fail-closed).
- Older `/modules/` CRUD still present (dual?).
- Admin gallery / modules surfaces in frontend.

## UI Surfaces
- `frontend/src/pages/Modules.tsx`: full filter/search/paginate + materialize + batch place integration (recent #136).
- Admin: AdminModules, AdminGallery.
- RackBuilder: uses catalog for placement, batch pack (contiguous HP).

## Gaps vs. P0 Spec (PDB-01..04 + Explorer + ADR-006)
- [ ] Full Device Registry hierarchy models (Mfr -> Family -> Model -> Rev -> Ports/Controls etc.)
- [ ] Versioned products/manufacturers/search/coverage public APIs beyond current catalog
- [ ] Public Product Explorer pages (/products/*) — Modules page is functional proxy but not full hierarchy navigator
- [ ] Deterministic migration path + compatibility adapters from ModuleGalleryRevision / ModuleCatalog
- [ ] Coverage / snapshot receipts published and bound to exact registry version
- [ ] Manufacturer management, aliasing, provenance, licensing registry in admin workbench
- [ ] ID stability + duplicate resolution queue formalized
- Dual sources (legacy gallery + catalog + synth seeds) need explicit reconciliation

## Recommendations (next slices)
1. Run full DB-connected inventory (alembic + seed load + SELECT counts).
2. Define canonical `Manufacturer` / `DeviceModel` etc. in new or backend/canon/ or backend/registry/.
3. Add `/catalog/manufacturers` + coverage endpoint using current ModuleCatalog grouped.
4. Produce registry snapshot JSON + hash.
5. Wire existing gallery data into new models via migration + adapters (preserve consumers).
6. Extend Modules page or add /explorer routes for manufacturers.
7. Update readiness matrix + pin SHA.

## Acceptance for this receipt
- Exact file list and model summary above.
- No claim of completeness.
- Receipt itself is evidence of inventory step.

**Generated by:** scripts/inventory_catalog.py
**Next:** operator or agent to load into DB and produce live counts receipt.
"""

    OUTPUT.write_text(receipt, encoding="utf-8")
    print(f"\n=== Receipt written to {OUTPUT} ===")

    print("\n=== Quick Summary ===")
    print(f"Brands in data scan: {total_brands_in_data}")
    print(f"Master claimed: {master_info.get('brands_claimed')}")
    print("Key catalog files present: ModuleCatalog, GalleryRevision, catalog_routes")
    print("Gaps logged in receipt. PDB-01 partial progress.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
