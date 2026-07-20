# GitHub Actions Workflows

PatchHive gates every pull request with three independent workflows:

- `backend-tests.yml`: Python 3.11/3.12, PostgreSQL 15, Alembic upgrade, and the full backend suite.
- `code-quality.yml`: Ruff, Black, mypy, ESLint, TypeScript, Vitest, production build, and Playwright.
- `security.yml`: pip-audit, npm audit, Bandit medium/high findings, Gitleaks, and Python/npm CycloneDX SBOM artifacts.

## Local parity

```bash
cd backend
python -m pytest tests -q
ruff check canon evidence tests/unit
black --check canon evidence tests/unit
mypy canon/contracts.py canon/compiler.py canon/runes.py canon/downloads.py evidence/images.py
pip-audit
bandit -q -r . -ll -x ./tests,./alembic

cd ../frontend
npm run type-check
npm run lint
npm test -- --run
npm run build
npm run test:e2e
npm audit --audit-level=high
```

The PostgreSQL migration and acceptance checks need Docker or a native PostgreSQL service. CI is the authoritative environment when neither is available locally. No workflow deploys the application or activates production payments.
