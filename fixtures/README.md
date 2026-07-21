# PatchHive Fixtures

This directory holds canonical fixture data used by acceptance tests and demos.

## Golden Demo

`golden_demo_seed.json` defines the deterministic rig + seed used by both backend acceptance tests and UI Playwright smoke tests.

Update the file only when patch generation logic changes in a way that intentionally changes deterministic outputs. When updating, bump `fixture_version` and refresh `expected_hashes` using the seed script:

```bash
python scripts/seed_golden_demo.py --print-hashes
```

## Cases research ingest (2026)

| File | Role |
|------|------|
| `Cases4PatchHive.md` | Source research report (50 cases, master + power tables) |
| `cases_research_2026.json` | Parsed rows matching `cases` table / `CaseCreate` schema |

```bash
# Re-parse markdown → JSON
just cases-parse
# or: python3 scripts/parse_cases_research.py

# Validate against Pydantic CaseCreate only
just cases-dry-run

# Upsert into DB (requires DATABASE_URL + backend deps)
just cases-import --replace-source
```

Staging walkthrough: [docs/design/CASES_STAGING_BOOTSTRAP.md](../docs/design/CASES_STAGING_BOOTSTRAP.md).

**Schema notes:** First-class `format_family`, `capacity_unit`, `powered` columns (migration `20260721_case_format_columns`). Eurorack uses HP in `total_hp` / `hp_per_row`. Non-Eurorack capacity uses the same numeric fields with `capacity_unit`. Rail currents stay `null` when unspecified (fail-closed).
