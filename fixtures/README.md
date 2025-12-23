# PatchHive Fixtures

This directory holds canonical fixture data used by acceptance tests and demos.

## Golden Demo

`golden_demo_seed.json` defines the deterministic rig + seed used by both backend acceptance tests and UI Playwright smoke tests.

Update the file only when patch generation logic changes in a way that intentionally changes deterministic outputs. When updating, bump `fixture_version` and refresh `expected_hashes` using the seed script:

```bash
python scripts/seed_golden_demo.py --print-hashes
```
