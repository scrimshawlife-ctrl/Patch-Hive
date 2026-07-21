# Synth Catalog Research — PatchHive seed

Sealed research packet from Abraxas skill **`modular-synth-catalog-research`**
([PR #984](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/984)).

## Files

| Path | Role |
|------|------|
| `seed-phase2-v1.json` | Deterministic seed (brands + catalog rows + full-spec subset) |
| `seed-phase2-v1.sources.json` | Access basis / evidence policy packet |
| `brand-index-modulargrid.txt` | Phase 1 brand index (~700) |
| `phase2-major-br.md` | Phase 2 major-brand tables (audit source) |
| `PATCHHIVE_INTEGRATION.md` | Integration analysis notes |
| `master-catalog.md` | Research master catalog summary |
| `alternative-sources.md` | 20-source rotation notes |
| `receipts/` | Dry-run / import receipts |

## Admit into PatchHive

```bash
# Dry-run (writes receipt only when --receipt set)
cd backend && python -m integrations.synth_catalog_importer --dry-run \
  --receipt ../data/synth-catalog/receipts/seed-phase2-v1.dry-run.json

# Catalog + curated full-spec
python -m integrations.synth_catalog_importer

# Fill null HP from manufacturer-curated specs (never invent)
python -m integrations.synth_catalog_importer --enrich-hp

# Or justfile
just synth-catalog-import --dry-run
just synth-catalog-import
just synth-catalog-import -- --enrich-hp
```

## Provenance rules

- `source = SynthCatalogResearch`
- HP / power / depth remain **null** when research did not record them (never invent)
- Catalog dedupe by **slug**; full modules skip existing `(brand, name)` from any source

## Rebuild

```bash
python3 scripts/build_synth_catalog_seed.py \
  --source-dir ~/Documents/Abraxas-v2.0/skills/modular-synth-catalog-research/references
```
