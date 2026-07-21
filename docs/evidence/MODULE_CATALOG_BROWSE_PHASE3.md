# Module catalog browse + Phase 3 seed (2026-07-21)

## Package

| Piece | Change |
|-------|--------|
| Catalog browse | `hp_known` filter; stats `hp_stats.known/unknown/coverage_pct` |
| Materialize | `POST /api/modules/catalog/{slug}/materialize` (requires HP; never invent) |
| Phase 3 seed | `data/synth-catalog/seed-phase3-v1.json` (9 Instruo condensed modules) |
| Frontend | Modules gallery uses lightweight catalog + Prepare for rig |
| Tests | materialize + phase3 import (12 total with existing synth tests) |

## Staging admit (Phase 3)

```bash
python -m integrations.synth_catalog_importer \
  --seed ../data/synth-catalog/seed-phase3-v1.json --catalog-only
```

| Metric | Value |
|--------|------:|
| Phase 3 imported | 9 |
| `module_catalog` total | 408 |
| Instruo rows | 9 |
| HP known (unchanged) | 35 |

Receipt: `data/synth-catalog/receipts/seed-phase3-v1.staging-import.json`

## Operator notes

- Gallery cards with unknown HP show **HP unknown** and disable prepare.
- Prepare materializes a full `modules` row with `source=ModuleCatalog` when HP is known.
- Expand Phase 3 via `just synth-catalog-phase3-seed` as Hermes research adds brands.
