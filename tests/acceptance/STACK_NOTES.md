# PatchHive Acceptance Test Stack Notes

## Backend
- **Framework**: FastAPI (`backend/main.py`)
- **Test framework**: Pytest (existing in `backend/tests`)
- **App entrypoint**: `backend/main.py` exposes `app`
- **Test client**: FastAPI `TestClient` using dependency injection for DB session
- **DB layer**: SQLAlchemy 2.0 (`backend/core/database.py`)
- **Migrations**: Alembic (`backend/alembic`, `backend/alembic.ini`)

## Frontend
- **Framework**: React + Vite (`frontend`)
- **UI tests**: Playwright (`frontend/tests/ui`)

## Test DB
- **Strategy**: Testcontainers Postgres (per-suite container)
- **Migrations**: `alembic upgrade head` executed once per suite
- **Isolation**: Tables truncated between tests

## Seed fixture
- **Golden Demo**: `fixtures/golden_demo_seed.json`
- **Seeder**: `scripts/seed_golden_demo.py` (test/demo only)
