# PatchHive

PatchHive is a deterministic Eurorack **rig-intelligence and patch-book publishing system**. It converts a verified modular rig into immutable, explainable patch libraries and publication-ready exports without synthesizing audio or controlling hardware.

> **Canonical publishing invariant:** every published patch is complete, executable, and understandable on exactly one standalone page.

## Status (2026-07-21)

| Item | Value |
|------|--------|
| **Canon MVP on main** | **MERGED** via [PR #47](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/47) |
| **P1 credits/exports client** | **MERGED** via [PR #49](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/49) — MVP UI uses `/api/canon/*` |
| **P1 acceptance → canon ledger** | **MERGED** via [PR #51](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/51) |
| **P1 run DTO export bridge** | **MERGED** via [PR #54](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/54) |
| **main HEAD** | `72c9dcc13e4321ca9605b9a2209d7eca398ac965` |
| **Campaign issue** | [#46](https://github.com/scrimshawlife-ctrl/Patch-Hive/issues/46) — closed |
| **Open draft PR** | [#53](https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/53) one-page publishing docs (this lineage) |
| **Alembic head** | `20240928_fix_schema_gaps` |
| **CI on HEAD** | Backend Tests · Code Quality · Security — green |
| **Production deploy** | Not performed — payments remain test-mode only |
| **Next work** | [docs/CONTINUATION.md](docs/CONTINUATION.md) **P1 residual** (inventory dual-path; native canon runs) · [CURRENT_STATE.md](CURRENT_STATE.md) |

## Product contract

PatchHive enables a user to:

1. Build or import a rig through manual, photo-assisted, or hybrid ingestion.
2. Confirm uncertain module matches and preserve missing technical data as missing.
3. Create an immutable rig revision.
4. Generate an immutable run containing exactly one patch library.
5. Explore validated patches for free.
6. Compile each patch into one deterministic page.
7. Export PDF, SVG, JSON, or ZIP artifacts through an idempotent credit boundary.
8. Revisit earlier runs without mutating their generated artifacts.

PatchHive is a compiler and publishing system—not a preset marketplace, audio simulator, DSP engine, or hardware-control surface.

## Current posture

| Area | Status |
|---|---|
| Canonical MVP | Implemented on `main` |
| Rig revisions and deterministic runs | Implemented |
| Canonical `/api/canon/*` credits and exports | Implemented in test mode |
| One-page Patch Book Generator | Canonical specification established; implementation work remains |
| Production payments | Disabled |
| Production deployment | Not performed |
| Hardware activation | Explicitly out of scope |

For exact commit, migration, CI, and deployment posture, use [CURRENT_STATE.md](CURRENT_STATE.md). For ordered remaining work, use [docs/CONTINUATION.md](docs/CONTINUATION.md).

## One-page Patch Book Generator

The Patch Book Generator is the flagship publishing pipeline:

```text
CanonicalRig
  -> PatchGraph + PatchPlan + ValidationReport
  -> PatchPageSpec
  -> PageFitReport
  -> deterministic SVG page assets
  -> PatchBookManifest
  -> PDF / SVG / JSON / ZIP export
```

### Non-negotiable rules

- Exactly one patch per page.
- No continuation pages and no shared patch pages.
- A page must work independently of a facing page or QR target.
- Critical instructions, warnings, ordered connections, starting settings, and listening cues remain on-page.
- The compiler may select among approved page layouts, simplify secondary prose, decompose an over-complex concept into separately valid patches, or reject the patch.
- The compiler must never solve overflow by violating minimum typography, clipping content, hiding required instructions, or crossing the page boundary.
- SVG is the canonical technical rendering format; PDF and raster assets are derived outputs.
- Color is supplemental. Cable routes also require identifiers, labels, patterns, or direction markers.
- Output must remain legible in grayscale and at the target print size.

The full contract is defined in [docs/PATCH_BOOK_GENERATOR.md](docs/PATCH_BOOK_GENERATOR.md).

## Canonical model

```text
User
  -> Rig
    -> immutable RigRevision
      -> immutable Run
        -> exactly one PatchLibrary
          -> immutable Patches
            -> exactly one PatchPageSpec per published patch
```

Generated artifacts are immutable. Favorites, notes, and completion state are mutable overlays that never alter canonical patch content.

## Architecture

- **Frontend:** React, TypeScript, Vite
- **Backend:** FastAPI modular monolith
- **Canonical domain:** `backend/canon`
- **Persistence:** PostgreSQL in production; SQLite only as a fast unit-test adapter
- **Migrations:** SQLAlchemy + Alembic
- **Contracts:** versioned canonical models and deterministic JSON
- **Rendering:** deterministic graph/page rendering with SVG as the technical source format
- **Exports:** asynchronous, idempotent, manifest-bound artifact generation
- **Payments:** Stripe-compatible test-mode integration; production charging disabled

Provider-assisted vision is untrusted evidence acquisition. Canonical normalization, graph generation, validation, page compilation, hashing, and manifest construction must be deterministic for fixed normalized input, generator version, schema version, and seed.

## Repository map

```text
backend/canon/                 canonical contracts, compiler, runes, exports
backend/patchhive/             compatibility and operational implementation
frontend/                      product UI
schemas/                       versioned schemas
patchhive/                     retained package and compatibility surfaces
docs/PATCH_BOOK_GENERATOR.md   publishing and one-page compiler contract
docs/PATCH_ENGINE.md           patch-generation contract and implementation notes
docs/CANON.md                  adopted canonical entries
docs/CONTINUATION.md           prioritized remaining work
docs/OPERATIONS.md             release, recovery, and production gates
```

## Quick start

### Prerequisites

- Python 3.11 or 3.12
- Node.js 22
- npm 10+
- PostgreSQL 15 for integration and migration testing
- Docker optional

### Backend

```bash
git clone https://github.com/scrimshawlife-ctrl/Patch-Hive.git
cd Patch-Hive
python3 -m venv .venv
source .venv/bin/activate
cd backend
python -m pip install -e '.[dev]'
alembic upgrade head
uvicorn main:app --reload
```

When a global tool injects `PYTHONPATH`, run project commands with a scrubbed environment:

```bash
env -u PYTHONPATH python -m pytest tests -q
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Copy `.env.example` to `.env`. Never deploy with repository development secrets or enable production payments without an explicit release decision.

Docker-oriented targets are available through `make dev`, `make test`, and `make db-migrate`.

## Validation

```bash
cd backend
python -m pytest tests --ignore=tests/acceptance -q
python -m ruff check canon evidence core/security.py tests
python -m mypy canon/contracts.py canon/compiler.py canon/runes.py canon/downloads.py evidence/images.py
alembic heads
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

A missing PostgreSQL or container service is `NOT_COMPUTABLE`, never a passing result. CI is authoritative only for the exact commit it evaluates.

### Patch-book release gates

### Validation snapshot (canon MVP)

| Gate | Result |
|------|--------|
| Main CI @ product path through PR #54 | SUCCESS (Backend 3.11/3.12 · Quality · Security) |
| Frontend unit | 51 passed |
| Playwright MVP | 4 passed |
| Acceptance without Docker/Postgres | `NOT_COMPUTABLE` locally — green path is CI |
| Golden compile hash | `c2356d416b9784d4487ffadf1fc6aafb974644f0767a5a36cba44d7f397934ee` |

A publishing build cannot ship unless all of the following pass:

- one patch produces exactly one page
- no required block overflows or clips
- minimum print and digital typography is preserved
- ordered connections and diagram encode the same graph
- all cross-references resolve
- grayscale and non-color interpretation remain usable
- deterministic replay produces byte-equivalent canonical JSON and stable SVG structure
- PDF page count matches the manifest
- each page binds to patch ID, patch version, source run, generator version, and canonical hash

## Documentation authority

| Document | Responsibility |
|---|---|
| [CURRENT_STATE.md](CURRENT_STATE.md) | Live repository and deployment posture |
| [docs/PATCH_BOOK_GENERATOR.md](docs/PATCH_BOOK_GENERATOR.md) | Canonical one-page publishing contract |
| [docs/PATCH_ENGINE.md](docs/PATCH_ENGINE.md) | Patch generation and validation |
| [docs/CANON.md](docs/CANON.md) | Adopted canon entries |
| [docs/CONTINUATION.md](docs/CONTINUATION.md) | Ordered implementation work |
| [docs/CANON_ALIGNMENT.md](docs/CANON_ALIGNMENT.md) | Active, transitional, legacy, and excluded surfaces |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Persistence and entity model |
| [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md) | WCAG and non-visual requirements |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Release gates and failure recovery |
| [docs/SECURITY.md](docs/SECURITY.md) | Trust boundaries and supply-chain controls |

Historical root notes may remain for provenance but are not ship authority unless referenced by `CURRENT_STATE.md` or the documents above.

## Safety and scope

PatchHive produces symbolic and technical documentation, not electrical certification. Unknown voltage, current, power, impedance, mode, or port behavior stays unknown until confirmed. Generated warnings are evidence-bound and must not be represented as universal hardware guarantees.

Community feeds, public profiles, comments, leaderboards, subscriptions, realtime collaboration, audio simulation, MIDI/CV activation, and hardware control remain outside the canonical MVP.

## Contributing

Before changing canonical behavior:

1. Pin the baseline commit and toolchain.
2. Identify the affected contract and invariant.
3. Update tests with the implementation.
4. Preserve deterministic serialization and append-only provenance.
5. Run the relevant validation suite.
6. Record unresolved risks as `NOT_COMPUTABLE` rather than inventing evidence.
7. Use a branch and pull request; do not deploy or activate production integrations implicitly.

## License

MIT.