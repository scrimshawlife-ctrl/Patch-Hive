# Operations and deployment

PatchHive remains a modular monolith. Apply the single Alembic head before application rollout, then start the FastAPI and static frontend processes. Production persistence is PostgreSQL; SQLite is a unit-test adapter only.

**Campaign note (2026-07-21):** No production deployment was performed on PR #47 or #49. Main HEAD `71a4dfa` is CI-green; staging may be stood up using the gates below. See [CONTINUATION.md](CONTINUATION.md) P0–P3. Prefer `/api/canon/*` for export/credit clients; legacy PatchBook debit POST remains transitional until acceptance migrates.

## Release gates

1. Install exactly from `backend/pyproject.toml` / `backend/requirements.txt` and `frontend/package-lock.json`.
2. Run backend, frontend, property/contract, security, and accessibility automation (or rely on green PR CI).
3. Run `alembic heads` and require exactly **`20240928_fix_schema_gaps`** (revises `20240927_canon_alignment`).
4. Run PostgreSQL integration and migration tests (`alembic upgrade head` against Postgres 15).
5. Generate and retain Python/npm CycloneDX SBOMs and build provenance (Security workflow artifacts).
6. Run ledger reconciliation (`reconcile_ledger` or equivalent admin path) and require no anomalies.
7. Verify all legacy feature flags are false (`ENABLE_LEGACY_SOCIAL`, `ENABLE_LEGACY_PUBLISHING`, `ENABLE_LEGACY_LEADERBOARDS`, `ENABLE_LEGACY_REFERRALS`).
8. Verify `STRIPE_TEST_MODE=true` and `ALLOW_PRODUCTION_PAYMENTS=false`.
9. Perform the manual accessibility protocol ([ACCESSIBILITY.md](ACCESSIBILITY.md)).
10. Confirm CORS, `SECRET_KEY`, and DB networking meet [SECURITY.md](SECURITY.md).

## Local / Compose

```bash
# Optional Docker path
make dev
make db-migrate
make test
```

Environment template: repository root `.env.example`. Never commit real secrets.

## Failure recovery

- A terminal export failure creates one immutable reversal keyed to the export and changes the mutable export state to refunded.
- Repeated export requests return the existing idempotent export and do not debit again.
- Replayed Stripe events with identical payloads are no-ops; a payload mismatch for the same event ID is rejected.
- Generation never overwrites a prior run; retry orchestration must create or resume an explicit job and preserve receipts.
- Prefer `/api/canon/*` for new export/credit clients; treat legacy `/api/export` as transitional until CONTINUATION P1 completes.

## CI authority

| Workflow | Role |
|----------|------|
| `backend-tests.yml` | Python 3.11/3.12 + PostgreSQL 15 + full backend suite |
| `code-quality.yml` | Ruff, Black, mypy, ESLint, tsc, Vitest, build, Playwright |
| `security.yml` | pip-audit, npm audit, Bandit, Gitleaks, CycloneDX SBOMs |

No workflow deploys the application or activates production payments.

## Deploy targets (inventory only)

Historical packaging exists for Render, Azure, Docker Compose, Fly/Railway snippets, and Replit export. None are certified “production ready” by this document without a fresh gate pass on the post-merge SHA. Ignore root `DEPLOY_STATUS.md` (2025-11) as ship authority.
