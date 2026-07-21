# Case catalog seed-v1 staging import (2026-07-21)

## Target

Local staging stack (`docker-compose.staging.yml`):

- Postgres: `patchhive-staging-db` @ `localhost:5432`
- Database: `patchhive`
- Backend rebuilt from `main` after import

## Pre-import schema work

Staging previously had application tables but **no** `alembic_version` and no case-catalog tables.

1. `alembic stamp 20240930_patch_user_overlays` (schema already matched that floor)
2. `alembic upgrade head` → `20260721_case_format_columns`

Applied:

- design engine export columns
- user style recipes
- modular case catalog tables
- case source policy packets
- legacy `cases` format columns (`format_family`, `capacity_unit`, `powered`)

## Import command

```bash
export DATABASE_URL='postgresql://patchhive:***@localhost:5432/patchhive'
cd backend
python -m integrations.case_catalog_populator \
  --input ../data/cases/seed-v1.json \
  --receipt ../data/cases/receipts/seed-v1.staging-import.json
```

## Receipt

```json
{
  "dry_run": false,
  "input_path": "../data/cases/seed-v1.json",
  "input_records": 50,
  "input_sha256": "74eb150b5825f7f403411215d8ce21911473957b1d31cace5f576af8130c8525",
  "inserted": 50,
  "rejected": 0,
  "status": "success",
  "updated": 0,
  "warnings": []
}
```

Persisted: `data/cases/receipts/seed-v1.staging-import.json`

## Post-import verification (SQL)

| Table | Count |
|-------|------:|
| case_catalog | 50 |
| case_revisions | 50 |
| case_rows | 73 |
| case_power_systems | 50 |
| case_sources | 635 |
| case_source_policy_packets | 635 |
| case_prices | 32 |

Format families: eurorack 36 · buchla_200 7 · serge_4u 3 · mu_5u 3 · frac 1

## Live API checks (after backend rebuild)

- `GET /health` → healthy
- `GET /api/cases/catalog/stats` → `case_count: 50`, `source_packet_count: 635`
- `GET /api/cases/catalog?format_family=eurorack&limit=3` → 36 total
- `POST /api/cases/catalog/4ms-pod20-powered/materialize` → legacy case bridge OK

## Publication note

Seed remains `research_candidate_not_verified_canonical`. Not manufacturer-verified truth.

## Operator UI

- API: http://localhost:8000
- App: http://localhost:5173 (frontend rebuilt from current `main` when this receipt was written)
- Cases page: `/cases` against catalog endpoints
