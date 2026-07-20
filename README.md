# PatchHive

PatchHive is a deterministic Eurorack **rig and patch documentation** workspace. The canonical MVP helps a user establish a module inventory, preserve immutable rig revisions, generate immutable patch-library runs, inspect safety findings, and purchase exports. It does **not** synthesize audio or control hardware.

## Status (2026-07-20)

| Item | Value |
|------|--------|
| **Active work** | Canon MVP alignment campaign |
| **Branch** | [`codex/patchhive-oneshot-canon-alignment`](https://github.com/scrimshawlife-ctrl/Patch-Hive/tree/codex/patchhive-oneshot-canon-alignment) |
| **PR** | [#47 — feat: align PatchHive canonical MVP](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/47) (draft, mergeable, CI green) |
| **Issue** | [#46 — PATCHHIVE_ONESHOT_CANON_ALIGNMENT_001](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) |
| **Baseline main** | `9cae772` (pre-canon; social-heavy surface) |
| **Campaign HEAD** | `1ab518c` |
| **Alembic head** | `20240928_fix_schema_gaps` |
| **Production deploy** | Not performed — payments remain test-mode only |
| **Next work** | [docs/CONTINUATION.md](docs/CONTINUATION.md) · [CURRENT_STATE.md](CURRENT_STATE.md) |

> **Note:** If you are on `main` before PR #47 merges, this README describes the **campaign target**. Prefer checking out the campaign branch for the canonical codebase.

## Canonical MVP

- Module and case catalogs with explicit provenance and missing-value preservation
- Manual rig building plus reviewable photo evidence
- Immutable hierarchy: user → rig → rig revision → run → exactly one patch library → generated patches
- Deterministic canonical JSON, stable hashes, run receipts, manifests, and replay tests
- Patch graph, five-phase plan (`prep`, `threshold`, `peak`, `release`, `seal`), deterministic variations, and validation report
- Responsive instrument-bench workspace with light/dark themes and an accessible graph/table pair
- PDF, SVG, JSON, and ZIP-capable export infrastructure; exploration remains free and credits apply at export
- Canonical HTTP surface under `/api/canon/*` (credits, exports, download tokens, Stripe-style webhooks in test mode)
- Admin diagnostics and immutable canonical audit records

Community feeds, public profiles, comments, votes, following, publishing, leaderboards, referrals, and contests are **not** active MVP features. Retained historical code is disabled by default and classified in [Canon alignment](docs/CANON_ALIGNMENT.md).

## Stack and boundaries

- FastAPI modular monolith; pure canonical domain logic lives in `backend/canon`
- SQLAlchemy/Alembic with PostgreSQL in production and SQLite for fast unit tests
- React, TypeScript, and Vite
- REST only; no GraphQL, microservices, DSP, MIDI/CV activation, or hardware control
- Provider detection is untrusted evidence acquisition and is isolated from deterministic compilation
- Stripe integrations are **test-mode only**; production payments are disabled

## Quick start

Prerequisites: Python 3.11 or 3.12, Node 22, npm 10+, PostgreSQL 15 for integration tests, and optionally Docker.

```bash
git clone https://github.com/scrimshawlife-ctrl/Patch-Hive.git
cd Patch-Hive
git checkout codex/patchhive-oneshot-canon-alignment   # until PR #47 merges

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

Useful Make targets (Docker Compose): `make dev`, `make test`, `make db-migrate` — see `Makefile`.

## Validation

```bash
cd backend
python -m pytest tests --ignore=tests/acceptance -q
python -m ruff check canon evidence core/security.py tests/unit/test_canon_*.py tests/unit/test_image_evidence.py
python -m mypy canon/contracts.py canon/compiler.py canon/runes.py canon/downloads.py evidence/images.py
alembic heads   # expect: 20240928_fix_schema_gaps
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

PostgreSQL integration and live migration checks require PostgreSQL or Docker. A missing service is reported as `NOT_COMPUTABLE`, never as a pass. CI (`.github/workflows/`) provisions PostgreSQL 15 and is authoritative when local containers are unavailable. The deterministic Playwright workspace suite uses isolated API fixtures and needs no production services.

### Campaign validation snapshot

| Gate | Result |
|------|--------|
| Backend unit/api (local, acceptance excluded) | 144 passed, 2 xfailed |
| Frontend unit | 49 passed |
| Playwright MVP | 4 passed |
| PR CI (3.11/3.12, quality, security) | Green on HEAD |
| Acceptance without Docker/Postgres | `NOT_COMPUTABLE` locally — green path is CI |
| Golden compile hash | `c2356d416b9784d4487ffadf1fc6aafb974644f0767a5a36cba44d7f397934ee` |

## Documentation

| Doc | Purpose |
|-----|---------|
| [CURRENT_STATE.md](CURRENT_STATE.md) | Live posture, HEAD, CI, boundaries |
| [docs/CONTINUATION.md](docs/CONTINUATION.md) | Ordered next work (P0–P5) |
| [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md) | Surface classification inventory |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture (+ canon notice) |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Persistence model |
| [docs/PATCH_ENGINE.md](docs/PATCH_ENGINE.md) | Compiler / generation |
| [docs/FEATURE_FLAGS.md](docs/FEATURE_FLAGS.md) | Legacy + payment flags + `/api/canon` routes |
| [docs/SECURITY.md](docs/SECURITY.md) | Trust boundaries and supply chain |
| [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md) | A11y expectations |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Release gates and recovery |
| [docs/VALIDATION_EVIDENCE.md](docs/VALIDATION_EVIDENCE.md) | Workflow screenshots |
| [docs/adr/0001-canonical-immutable-hierarchy.md](docs/adr/0001-canonical-immutable-hierarchy.md) | Hierarchy ADR |

**Superseded root notes** (do not use as ship authority): `CANON_DIFF.md`, `CANON_SYNC.md`, `DEPLOY_STATUS.md` (2025-11). Prefer CURRENT_STATE + CONTINUATION.

Replit-oriented packaging notes remain in [README_REPLIT.md](README_REPLIT.md) and `STRIPE_INTEGRATION_PROMPT.md` (implementation prompt only — not live billing).

## Safety and status

PatchHive provides symbolic documentation, not an electrical safety certification. Missing voltage, power, mode, or port specifications remain missing and require confirmation. Development and tests never activate production Stripe, deploy production, charge customers, or control hardware.

License: MIT.
