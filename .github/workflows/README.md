# GitHub Actions Workflows

PatchHive gates pull requests with independent workflows:

- `backend-tests.yml`: Python 3.11/3.12, PostgreSQL 15, Alembic upgrade, unit/api suite (excludes acceptance).
- `acceptance-tests.yml`: Golden-path acceptance via `scripts/test/run.sh acceptance` + Postgres service (`ACCEPTANCE_DATABASE_URL`).
- `code-quality.yml`: Ruff, Black, mypy, ESLint, TypeScript, Vitest, production build, and Playwright.
- `engineering-quality.yml`: Extended unit/docs/import-guard gates.
- `security.yml`: pip-audit, npm audit, Bandit medium/high findings, Gitleaks, and Python/npm CycloneDX SBOM artifacts.

## Local parity

```bash
# Preferred unified runner
bash scripts/test/run.sh ci              # unit + frontend + acceptance
# powershell -File scripts/test/run.ps1 ci

# Or piecemeal
bash scripts/test/run.sh unit
bash scripts/test/run.sh acceptance
bash scripts/test/run.sh frontend
bash scripts/test/run.sh e2e
bash scripts/test/run.sh staging         # compose smoke + acceptance DB + design-engine

cd backend
ruff check canon evidence tests/unit
black --check canon evidence tests/unit
pip-audit
bandit -q -r . -ll -x ./tests,./alembic

cd ../frontend
npm run type-check
npm run lint
npm run build
npm audit --audit-level=high
```

Acceptance uses Testcontainers when `ACCEPTANCE_DATABASE_URL` is unset; CI and compose scripts set that URL explicitly. No workflow deploys the application or activates production payments.
