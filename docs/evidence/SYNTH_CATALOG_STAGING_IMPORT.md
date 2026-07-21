# Synth Catalog Research — staging admit (2026-07-21)

## Target

Local staging stack (`docker-compose.staging.yml`):

- Postgres: `patchhive-staging-db` @ `localhost:5432`
- Database: `patchhive`
- Importer: host `main` / follow-up branch against staging `DATABASE_URL`

## Pre-state

| Table | Count |
|-------|------:|
| `module_catalog` | 0 |
| `modules` | 17 |

## Actions

### 1. Durable seed import (`#113`)

```bash
export DATABASE_URL='postgresql://patchhive:***@localhost:5432/patchhive'
cd backend
python -m integrations.synth_catalog_importer --dry-run \
  --receipt ../data/synth-catalog/receipts/seed-phase2-v1.staging-dry-run.json
python -m integrations.synth_catalog_importer \
  --receipt ../data/synth-catalog/receipts/seed-phase2-v1.staging-import.json
```

| Metric | Value |
|--------|------:|
| Catalog imported | 376 |
| Catalog skipped | 0 |
| Full-spec imported | 2 |
| Full-spec skipped | 1 (Make Noise Maths already present from another source) |
| Seed SHA-256 | `e7e7a57d2e843add1d6414f6ddc86e853ce9e15c52fff3457dc5eb3ec36ee59d` |

### 2. Curated ModularGrid → catalog

```bash
python -c 'from core.database import SessionLocal; from integrations.catalog_populator import populate_catalog_from_curated_modules; db=SessionLocal(); print(populate_catalog_from_curated_modules(db))'
```

| Metric | Value |
|--------|------:|
| Curated catalog imported | 23 |
| Skipped (already present) | 9 |

### 3. HP enrich (manufacturer-confirmed only)

```bash
python -m integrations.synth_catalog_importer --enrich-hp \
  --receipt ../data/synth-catalog/receipts/seed-phase2-v1.staging-hp-enrich.json
```

Sources: `MODULES_DATABASE` + existing `modules` rows with non-null `hp`.  
Never invents; never overwrites non-null catalog HP.

| Metric | Value |
|--------|------:|
| Known specs | 42 |
| Examined null/UTIL rows | 372 |
| HP updated | 8 |
| Category refined | 2 |

Examples: Maths 20 HP, DPO 30, Morphagene 18, Ripples 8, Quad VCA 12, Rampage 18, A-140 8, Pico DSP 3.

## Post-state

| Table / metric | Count |
|----------------|------:|
| `module_catalog` | 399 |
| `module_catalog` with HP | 35 |
| `modules` total | 19 |
| `modules` source=SynthCatalogResearch | 2 |

## Receipts

- `data/synth-catalog/receipts/seed-phase2-v1.staging-dry-run.json`
- `data/synth-catalog/receipts/seed-phase2-v1.staging-import.json`
- `data/synth-catalog/receipts/seed-phase2-v1.staging-hp-enrich.json`

## Notes

- Staging backend container was **not** rebuilt for this admit; import used host code against staging Postgres (data-only).
- Rebuild/redeploy staging backend when operators need live `/api/synth-catalog/*` on the container (code is on `main` + enrich PR).
- Remaining null HP rows require manufacturer-confirmed research enrichment (Phase 2 tables were sparse on HP).
