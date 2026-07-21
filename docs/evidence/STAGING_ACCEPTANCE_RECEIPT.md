# Staging acceptance receipt

**Date:** 2026-07-21  
**Branch:** `grok/patchhive-visual-system-canon-audit`  
**Alembic head:** `20240929_visual_inventory_evidence`

## Intent

Run backend acceptance against Postgres (testcontainers) to clear local
`NOT_COMPUTABLE` for dual-path credits/export golden paths.

## Environment

| Item | Value |
|------|--------|
| Host OS | macOS |
| Docker | available (OBSERVED) |
| Method | `pytest tests/acceptance` with testcontainers |

## Results

```yaml
acceptance:
  command: "cd backend && env -u PYTHONPATH python -m pytest tests/acceptance -q"
  result: "11 passed"
  class: OBSERVED
  notes:
    - testcontainers Postgres used by suite
    - no production credentials
unit_api:
  command: "cd backend && env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance -q"
  result: "189 passed, 2 xfailed"
  class: OBSERVED
frontend:
  command: "npm test -- --run && npm run type-check"
  result: "51 passed; tsc clean"
  class: OBSERVED
compose_full_stack:
  result: NOT_COMPUTABLE  # full make test / multi-service stack not required for this receipt
production_deploy:
  result: NOT_PERFORMED
```
