# PatchHive

PatchHive is a deterministic Eurorack rig and patch documentation workspace. The canonical MVP helps a user establish a module inventory, preserve immutable rig revisions, generate immutable patch-library runs, inspect safety findings, and purchase exports. It does not synthesize audio or control hardware.

## Canonical MVP

- Module and case catalogs with explicit provenance and missing-value preservation
- Manual rig building plus reviewable photo evidence
- Immutable hierarchy: user → rig → rig revision → run → exactly one patch library → generated patches
- Deterministic canonical JSON, stable hashes, run receipts, manifests, and replay tests
- Patch graph, five-phase plan (`prep`, `threshold`, `peak`, `release`, `seal`), deterministic variations, and validation report
- Responsive instrument-bench workspace with light/dark themes and an accessible graph/table pair
- PDF, SVG, JSON, and ZIP-capable export infrastructure; exploration remains free and credits apply at export
- Admin diagnostics and immutable canonical audit records

Community feeds, public profiles, comments, votes, following, publishing, leaderboards, referrals, and contests are not active MVP features. Their retained historical code is disabled by default and classified in [Canon alignment](docs/CANON_ALIGNMENT.md).

## Stack and boundaries

- FastAPI modular monolith; pure canonical domain logic lives in `backend/canon`
- SQLAlchemy/Alembic with PostgreSQL in production and SQLite for fast unit tests
- React, TypeScript, and Vite
- REST only; no GraphQL, microservices, DSP, MIDI/CV activation, or hardware control
- Provider detection is untrusted evidence acquisition and is isolated from deterministic compilation
- Stripe integrations are test-mode only; production payments are disabled

## Quick start

Prerequisites: Python 3.11 or 3.12, Node 22, npm 10+, PostgreSQL 15 for integration tests, and optionally Docker.

```bash
python3 -m venv .venv
source .venv/bin/activate
cd backend
python -m pip install -e '.[dev]'
alembic upgrade head
uvicorn main:app --reload
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Copy `.env.example` to `.env`. Never use the checked-in development secret in a deployed environment.

## Validation

```bash
cd backend
python -m pytest tests --ignore=tests/acceptance -q
python -m ruff check canon evidence core/security.py tests/unit/test_canon_*.py tests/unit/test_image_evidence.py
python -m mypy canon/contracts.py canon/compiler.py canon/runes.py canon/downloads.py evidence/images.py
python -m pip_audit
python -m bandit -q -ll -r . -x ./tests,./patchhive/tests,./patchhive/runes/tests

cd ../frontend
npm ci
npm run lint
npm run type-check
npm test -- --run
npm run build
npx playwright install chromium
npm run test:e2e
npm audit --audit-level=high
```

PostgreSQL integration and live migration checks require PostgreSQL or Docker. A missing service is reported as `NOT_COMPUTABLE`, never as a pass. The deterministic Playwright workspace suite uses isolated API fixtures and needs no production services.

## Documentation

- [Canon alignment and inventory](docs/CANON_ALIGNMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model](docs/DATA_MODEL.md)
- [Patch compiler](docs/PATCH_ENGINE.md)
- [Feature flags](docs/FEATURE_FLAGS.md)
- [Security](docs/SECURITY.md)
- [Accessibility](docs/ACCESSIBILITY.md)
- [Operations and deployment](docs/OPERATIONS.md)
- [Validation evidence and workflow screenshots](docs/VALIDATION_EVIDENCE.md)
- [Canonical migration ADR](docs/adr/0001-canonical-immutable-hierarchy.md)

## Safety and status

PatchHive provides symbolic documentation, not an electrical safety certification. Missing voltage, power, mode, or port specifications remain missing and require confirmation. Development and tests never activate production Stripe, deploy production, charge customers, or control hardware.

License: MIT.
