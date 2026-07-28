# Staging acceptance suite receipt

```yaml
date: "2026-07-26"
method: scripts/staging/acceptance.ps1
database: patchhive_acceptance on compose Postgres (port 5433)
compose: docker-compose.staging.yml
result: PASS
payments:
  STRIPE_TEST_MODE: true
  ALLOW_PRODUCTION_PAYMENTS: false
```

## Procedure

1. Staging stack up (`db` healthy).  
2. Create dedicated DB `patchhive_acceptance` (does not truncate live staging API DB).  
3. Host venv `backend/.venv-acceptance` with `pip install -e '.[dev]'`.  
4. `ACCEPTANCE_DATABASE_URL=postgresql://…@localhost:5433/patchhive_acceptance`  
5. `pytest tests/acceptance -q`

## OBSERVED

```
11 passed, 626 warnings in 46.78s
```

| Module | Tests |
|--------|-------|
| `test_admin_ops.py` | admin audit, pending functions, non-admin denied |
| `test_exports_and_credits.py` | credits gate, admin grant + export, compensate |
| `test_golden_path.py` | multi-rig, golden fingerprint, deterministic generate, naming, run history |

## Code

- `ACCEPTANCE_DATABASE_URL` / `STAGING_DATABASE_URL` skips Testcontainers (`backend/tests/acceptance/conftest.py`)
- `ACCEPTANCE_EXPORT_DIR` avoids Windows `%TEMP%` permission issues

## Re-run

```powershell
powershell -File scripts/staging/smoke.ps1 -SkipBuild   # optional
powershell -File scripts/staging/acceptance.ps1
```

**Authority:** local staging Postgres only — not named multi-tenant host.
