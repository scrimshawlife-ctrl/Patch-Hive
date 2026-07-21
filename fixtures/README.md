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
python3 scripts/parse_cases_research.py

# Validate against Pydantic CaseCreate only
python3 scripts/import_cases_research.py --dry-run

# Upsert into DB (requires DATABASE_URL + backend deps)
python3 scripts/import_cases_research.py
# optional: delete prior ResearchCSV rows first
python3 scripts/import_cases_research.py --replace-source
```

**Schema notes:** Eurorack uses HP in `total_hp` / `hp_per_row`. Buchla / Serge / MU / Frac store capacity in those columns with `meta.capacity_unit`. Rail currents stay `null` when the research source marked them unspecified (fail-closed).
