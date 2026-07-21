# `patchhive` package import telemetry

**Method:** `rg` over `backend/**/*.py` after AI foundation indexes (`just memory`)  
**Date:** 2026-07-21 · main @ `b117848`  
**Goal:** Classify imports so agents do not confuse HISTORICAL `backend/patchhive` with CANON_MVP `backend/canon`.

## Classification

| Class | Meaning | Disposition |
|-------|---------|-------------|
| **CANON_MVP** | `backend/canon/*` | Primary authority |
| **CANON_SUPPORTING** | Pipeline still used by tests/export paths under `backend/patchhive` | Keep until dual-write complete |
| **HISTORICAL_TEST** | Unit tests importing v1 schemas/pipeline | Quarantine discovery optionally |
| **NO_IMPORT_FROM_CANON** | `backend/canon` must not import `patchhive` package | **PASS** (only string schema versions) |

## Evidence

### `backend/canon` → `patchhive` package

```text
No `from patchhive` / `import patchhive` in backend/canon
(Only schema_version strings containing "patchhive.")
```

**Exit criterion met for “no accidental canon→patchhive imports”.**

### Heaviest importers (file match counts, approximate)

| File | Import lines (rg -c) | Class |
|------|----------------------|-------|
| `backend/tests/unit/test_query_surface.py` | 9 | HISTORICAL_TEST |
| `backend/patchhive/pipeline/run.py` | 8 | CANON_SUPPORTING |
| `backend/patchhive/cli/export_pack.py` | 8 | CANON_SUPPORTING |
| `backend/patchhive/ops/build_patch_library.py` | 7 | CANON_SUPPORTING |
| `backend/tests/unit/test_export_pack.py` | 6 | HISTORICAL_TEST |
| `backend/patchhive/*` internal | many | Self-contained historical subsystem |

### Packaging

`backend/pyproject.toml` still lists `patchhive*` packages and `testpaths` includes `patchhive/runes/tests`.

## Recommended next slices (do not big-bang delete)

1. **Docs-only (this file)** — agents know classification  
2. **pytest norecursedirs / path markers** — optional exclude pure historical tests from default `pytest tests` if already isolated  
3. **No new features in `backend/patchhive`** — implement on `canon` / `evidence` / `patches`  
4. **Later PR:** move remaining pipeline consumers or dual-write then drop package  

## Agent rule

```text
Prefer backend/canon and backend/evidence for new work.
Treat backend/patchhive as read-mostly historical pipeline unless fixing a red test.
```
