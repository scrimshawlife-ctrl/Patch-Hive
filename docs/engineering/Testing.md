# Testing

## Backend

```bash
cd backend
# Unit + API (no acceptance / no Docker required for most)
env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance -q

# Acceptance (testcontainers / Docker)
env -u PYTHONPATH python -m pytest tests/acceptance -q

# Coverage
env -u PYTHONPATH python -m pytest tests --ignore=tests/acceptance --cov -q
```

Compose-based: `make test` (requires Docker Desktop + running stack).

## Frontend

```bash
cd frontend
npm test -- --run
npm run type-check
npm run lint
npm run build
CI=1 npm run test:e2e   # Playwright; avoid stale Vite with CI=1
```

## Quality gates

```bash
cd backend
ruff check canon evidence
black --check canon evidence
mypy canon/contracts.py canon/compiler.py  # expand as needed
```

## Evaluation (vision)

```bash
pytest backend/tests/unit/test_vision_evaluation.py -q
```

Production accuracy remains **NOT_COMPUTABLE** without a licensed representative dataset.

## Policy

- CI is authoritative when local Postgres/Docker missing
- Do not fabricate test results
- Prefer fixtures and mock vision providers over live paid models
