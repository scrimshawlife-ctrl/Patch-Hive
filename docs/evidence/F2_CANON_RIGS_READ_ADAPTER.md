# F2 — Thin `GET /api/canon/rigs` read adapter

**Date:** 2026-07-26  
**Slice:** dual-path residual **F2** ([DUAL_PATH_RETIREMENT_DESIGN.md](DUAL_PATH_RETIREMENT_DESIGN.md))  
**Authority:** OBSERVED tests; no production deploy; no FE cutover forced

## Intent

Expose inventory rig list/detail under the canon prefix without renaming or deleting `/api/racks`.

| HTTP | Role |
|------|------|
| `GET /api/canon/rigs` | Paginated list; filters `is_public`, `user_id` |
| `GET /api/canon/rigs/{rig_id}` | Detail + modules/case (via `build_rack_response`) |
| `GET /api/canon/rigs/{rig_id}/revisions` | Unchanged (prior slice) |

**Honesty:** response always has `rig_id == rack_id` (integer rack primary key).

## Non-goals

- No POST/PATCH/DELETE under `/api/canon/rigs` (writes stay on `/api/racks`)
- No FE mandatory switch (optional `canonApi.listRigs` / `getRig`)
- No evidence dual-mount (F4)

## Tests

`backend/tests/api/test_canon_rigs_api.py` — list equality, public filter, detail modules, 404, revisions still mounted.

## Exit

F2 exit criteria met: thin read adapter live; FE can opt in later (F5).
