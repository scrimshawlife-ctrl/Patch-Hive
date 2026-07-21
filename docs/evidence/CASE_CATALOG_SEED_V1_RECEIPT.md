# Case catalog seed-v1 admission receipt (2026-07-21)

## Scope

Convert the researched 50-case list into the normalized case catalog seed, attach
field-level source-policy packets, publish the source/licensing manifest, and
produce a dry-run import receipt bound to the exact input SHA-256.

## Inputs

| Artifact | Path | SHA-256 |
|----------|------|---------|
| Research report | `fixtures/Cases4PatchHive.md` | `e310933e71469f97b13eda3e1132797c8dd298b28cc9a571848d39ff5c7335e3` |
| Parsed research fixture | `fixtures/cases_research_2026.json` | (see `seed-v1.sources.json`) |
| Canonical seed | `data/cases/seed-v1.json` | `2de4eab23d4975f07366b524d76babb9ef4a5d4b38222c301857274dd655d11f` |
| Source manifest | `data/cases/seed-v1.sources.json` | regenerated with seed |
| Coverage stats | `data/cases/seed-v1.coverage.json` | regenerated with seed |

Normalizer: `case-catalog-v1` via `scripts/build_case_catalog_seed.py`.

## Dry-run receipt

```json
{
  "dry_run": true,
  "input_path": "../data/cases/seed-v1.json",
  "input_records": 50,
  "input_sha256": "2de4eab23d4975f07366b524d76babb9ef4a5d4b38222c301857274dd655d11f",
  "inserted": 50,
  "rejected": 0,
  "status": "success",
  "updated": 0,
  "warnings": []
}
```

Persisted at `data/cases/receipts/seed-v1.dry-run.json`.

## Coverage summary

| Metric | Count | % of 50 |
|--------|------:|--------:|
| Eurorack | 36 | 72.0 |
| Buchla 200 | 7 | 14.0 |
| Serge 4U | 3 | 6.0 |
| MU/5U | 3 | 6.0 |
| Frac | 1 | 2.0 |
| +12V rail known | 22 | 44.0 |
| Depth known | 29 | 58.0 |
| Outer width known | 17 | 34.0 |
| Weight known | 17 | 34.0 |
| Price observation | 32 | 64.0 |
| Source packets present | 50 | 100.0 |

Field-level source packets: **635** (mean **12.7** per case).

## Publication state

`research_candidate_not_verified_canonical`

- Access basis: `manual_research`
- Evidence status: `UNKNOWN` (research synthesis, not manufacturer-confirmed)
- Review state: `pending`
- Unknown research cells remain `null`

This seed is admissible for catalog bootstrap and importer validation. It is
**not** manufacturer-verified canonical truth. Higher-authority official manuals
and product pages remain required for verified publication.

## Related validation

- Foundation validation (PR #100 head `3f2dc631…`): see
  `docs/evidence/CASE_CATALOG_FOCUSED_VALIDATION.md`
- Importer unit tests: `tests/test_case_catalog_populator.py`
- CI workflow: `.github/workflows/case-catalog-validation.yml` now dry-runs
  `seed-v1.json` and asserts the receipt SHA-256 matches the committed seed

## Follow-up

1. Broader repository CI on the seed admission PR
2. Case catalog read API
3. Rack Builder compatibility engine against catalog revisions
