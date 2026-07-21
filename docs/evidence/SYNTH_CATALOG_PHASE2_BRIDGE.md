# Evidence: Synth Catalog Research → PatchHive modules catalog

**Date:** 2026-07-21  
**Branch:** `feat/synth-catalog-module-bridge`  
**Source:** Abraxas `skills/modular-synth-catalog-research` ([PR #984](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/984))

## Goal

Consume Hermes/Abraxas modular-synth research into PatchHive’s two-tier module catalog so discovery is no longer limited to the ~32 curated ModularGrid full-spec rows.

## What landed

| Piece | Path |
|-------|------|
| Sealed seed | `data/synth-catalog/seed-phase2-v1.json` |
| Policy packet | `data/synth-catalog/seed-phase2-v1.sources.json` |
| Data loader | `backend/integrations/synth_catalog_data.py` |
| Importer | `backend/integrations/synth_catalog_importer.py` |
| API | `GET/POST /api/synth-catalog/*` |
| Catalog populator flag | `python -m integrations.catalog_populator --synth-research` |
| Rebuild script | `scripts/build_synth_catalog_seed.py` |
| Tests | `backend/tests/test_synth_catalog.py` |
| Docs | `backend/DATA_SOURCES.md` §4, `data/synth-catalog/README.md` |

## Seed metrics (pinned)

- Brands (Phase 1 index): **703**
- Catalog modules (Phase 2 tables): **376**
- HP known in research tables: **4** (remainder null — never invented)
- Full-spec curated modules: **3** (Noise Engineering BIA, Make Noise Maths, Instruo arbhar)

## Verification

```text
cd backend && .venv/bin/python -m pytest tests/test_synth_catalog.py -q
# 7 passed
```

Dry-run + SQLite admit receipts:

- `data/synth-catalog/receipts/seed-phase2-v1.dry-run.json`
- `data/synth-catalog/receipts/seed-phase2-v1.import-sqlite.json`

## Provenance rules (ABX-Core)

- `source = SynthCatalogResearch`
- Catalog dedupe by **slug**; full modules skip any existing `(brand, name)`
- Null HP/power/depth when research did not record values
- Access basis: `manual_research` / `CATALOG_OBSERVED` (not a ModularGrid bulk dump)

## Follow-ups

1. ~~Staging admit against live Postgres~~ → see `SYNTH_CATALOG_STAGING_IMPORT.md`
2. ~~HP enrich from curated ModularGrid / modules table~~ → `--enrich-hp` / `POST /api/synth-catalog/enrich/hp`
3. ~~Rebuild staging backend + package seed for Docker~~ → #115
4. ~~Phase 3 partial seed + FE catalog browse + materialize~~ → seed-phase3-v1 + Modules gallery
5. Catalog API `source` column once needed for mixed-source filtering
6. Broader HP/power enrichment from manufacturer-confirmed research (Phase 2/3 still sparse)
7. Expand Phase 3 mid-tier as Hermes research completes more brands

## Operator commands

```bash
just synth-catalog-import -- --dry-run --receipt data/synth-catalog/receipts/operator.dry-run.json
just synth-catalog-import
curl -s localhost:8000/api/synth-catalog/stats | jq .
```
