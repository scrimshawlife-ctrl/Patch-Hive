# Catalog dual-gate rack writes (2026-07-21)

## Intent

When a legacy `cases` row is linked to the normalized catalog (`meta.catalog_slug`),
rack create/update runs **two** gates:

1. **Legacy** `validate_rack_configuration` (HP layout, known rails) — hard errors as before.
2. **Catalog** compatibility (`dual_gate_catalog_errors_and_warnings`)
   - `conflict` → hard 400 errors
   - `incomplete` → soft `validation_warnings` (missing specs; never invent capacity)
   - unlinked cases → dual-gate skipped (legacy only)

## Tests

- `tests/test_rack_dual_gate.py` — depth conflict hard-fails create/update; fitting module succeeds
- Existing catalog/rack bridge suites remain green

## Operator fixtures

```bash
export DATABASE_URL=...
just case-catalog-seed-import
just modules-demo-import
# optional:
curl -X POST "$API/api/cases/catalog/materialize-batch?format_family=eurorack"
```

## UI

- `/cases/:slug` detail (revisions, power, provenance, materialize CTA)
- Rack Builder / Racks still show advisory compatibility panels

## Issue hygiene

Implements residual P1 from main integration analysis after #103–#111.
