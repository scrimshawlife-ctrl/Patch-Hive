# F4 — Evidence path on canon prefix

**Date:** 2026-07-26  
**Slice:** dual-path residual **F4** ([DUAL_PATH_RETIREMENT_DESIGN.md](DUAL_PATH_RETIREMENT_DESIGN.md))  
**Authority:** OBSERVED tests; no production deploy

## Intent

Dual-mount multi-image evidence handlers under the canon inventory key without removing `/api/racks/{id}/evidence/*`.

| Legacy | Canon alias (same handler) |
|--------|----------------------------|
| `POST /api/racks/{id}/evidence/images` | `POST /api/canon/rigs/{id}/evidence/images` |
| `GET /api/racks/{id}/evidence/images` | `GET /api/canon/rigs/{id}/evidence/images` |
| `DELETE .../evidence/images/{asset_id}` | same under `/api/canon/rigs/{id}/...` |
| `GET .../evidence/candidates` | same |
| `GET .../evidence/reconcile` | same |
| `GET .../evidence/inventory` | same |
| `POST .../evidence/confirmations` | same |

**Honesty:** path param is still integer rack id (`rig_id ≡ rack_id`).

## FE

`evidenceApi` now calls the canon prefix paths. Legacy URLs remain valid for other clients.

## Tests

`backend/tests/api/test_canon_evidence_aliases.py` — upload/list/delete + candidates/reconcile/inventory on canon path; parity with racks list total.

## Non-goals

- F5 FE inventory list cutover to `canonApi.listRigs`
- Delete of `/api/racks` evidence paths
