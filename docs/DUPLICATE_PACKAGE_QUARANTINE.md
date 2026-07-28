# Duplicate package quarantine

Audit date: 2026-07-28, after commit `8c5ceb5`.

## Canonical package

- `backend/patchhive` is the canonical importable `patchhive` compatibility package for backend tests and packaging.
- `backend/pyproject.toml` includes `patchhive` and selected subpackages from `backend/patchhive` only.
- Canonical pytest discovery is scoped to `backend/tests` and `backend/patchhive/runes/tests`; the duplicate top-level `patchhive/tests` suite is not part of canonical backend discovery.

## Quarantined duplicate top-level packages

- `patchhive/` is a historical v1 tree with its own tests and CLIs. It shadows `backend/patchhive` whenever the repository root is placed before `backend` on `PYTHONPATH`.
- `patch_hive/patch_hive/` is a legacy underscored package retained with a manifest and small server/export helpers.
- `patchhive_overlay/` is a legacy Abraxas overlay service retained for explicit compatibility jobs.

## Active references found

- Backend package imports: `backend/patchhive/**`, `backend/patchhive/runes/tests/**`, and `backend/tests/unit/**` import `patchhive.*`. These are active compatibility imports and are expected to resolve to `backend/patchhive` when tests run from `backend` or with `backend` first on `PYTHONPATH`.
- Top-level duplicate tests: `patchhive/tests/**` import the top-level `patchhive.*` tree. They are historical compatibility tests and are not selected by `backend/pyproject.toml`.
- Packaging: `backend/pyproject.toml` packages `backend/patchhive` subpackages only. No packaging config includes top-level `patchhive`, `patch_hive`, or `patchhive_overlay`.
- Scripts and docs: historical docs mention `patchhive_overlay/server.py`; README validation excludes `patchhive/tests`; no production package script installs the duplicate top-level trees.

## Guardrail

Each duplicate top-level package now refuses import in production-like environments when one of `PATCHHIVE_ENV`, `APP_ENV`, `ENV`, or `ENVIRONMENT` is `prod`, `production`, or `staging`. Explicit compatibility jobs may set `PATCHHIVE_ALLOW_LEGACY_IMPORTS=1`.

This keeps compatibility code in place while preventing accidental production imports caused by repository-root `PYTHONPATH` shadowing.
