# PatchHive Acceptance Tests

This suite validates the MVP golden path end-to-end:

1. Create rig
2. Generate patch library
3. View patches
4. Export patch book (credit gated)
5. Admin controls

## Prerequisites

- Python 3.11
- Node 18+
- Docker (for Testcontainers)

## One command

```bash
make test-acceptance
```

## Backend acceptance tests

```bash
cd backend
python -m pytest tests/acceptance -q
```

## UI smoke tests (Playwright)

```bash
cd frontend
npm run test:e2e
```

Playwright requires browsers:

```bash
cd frontend
npx playwright install --with-deps
```

Environment variables for UI tests (optional):

- `PLAYWRIGHT_API_URL` (defaults to `http://localhost:8000/api`)
- `PLAYWRIGHT_DATABASE_URL` (for the Golden Demo seed script)

## Golden Demo fixture

The acceptance tests use the Golden Demo fixture located at `fixtures/golden_demo_seed.json`.

To reseed and refresh expected hashes (intentional changes only):

```bash
python scripts/seed_golden_demo.py --update-fixture
```

## CI snippet

```yaml
- name: Acceptance tests
  run: |
    make test-acceptance
```
