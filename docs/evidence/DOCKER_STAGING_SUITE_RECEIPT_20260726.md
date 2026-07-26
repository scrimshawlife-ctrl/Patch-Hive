# Docker staging suite receipt

```yaml
date: "2026-07-26"
method: scripts/staging/docker-suite.ps1
compose:
  - docker-compose.staging.yml
  - docker-compose.staging.acceptance.yml
  - docker-compose.staging.design-engine.yml
ports:
  api: 18000
  fe: 15173
  db: 5433
result: PASS
payments:
  STRIPE_TEST_MODE: true
  ALLOW_PRODUCTION_PAYMENTS: false
```

## Steps OBSERVED

| Step | Result |
|------|--------|
| Rebuild backend image + smoke | PASS — `/health/ready`, alembic head `20260726_module_registry_slugs` |
| Backup/restore side DB | PASS — `pg_dump` + `pg_restore` into `patchhive_restore_smoke` |
| F2 live probe `GET /api/canon/rigs` | PASS — list JSON with `rig_id == rack_id` |
| In-network acceptance (`acceptance` service) | PASS — **11 passed** |
| Design Engine walkthrough | PASS (see DESIGN_ENGINE_STAGING_ENABLEMENT_RECEIPT) |

## Commands

```powershell
powershell -File scripts/staging/docker-suite.ps1
# or:
powershell -File scripts/test/run.ps1 docker-suite
```

```bash
bash scripts/test/run.sh docker-suite
```

**Authority:** local Docker Compose only; named host NOT_PERFORMED.
