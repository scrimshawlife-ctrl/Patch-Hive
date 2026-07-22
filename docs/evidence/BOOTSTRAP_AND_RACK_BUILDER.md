# Bootstrap validation + Rack Builder UX (2026-07-22)

## 1. Staging bootstrap (idempotent)

**Method:** HP overlay SQL + `POST /api/modules/catalog/materialize-batch` + power overlays v1–v4 COALESCE.

| Metric | Before | After |
|--------|-------:|------:|
| Catalog total | 408 | 408 |
| HP known | 404 | **404 (99%)** |
| Modules total | 418 | 418 |
| ModuleCatalog rows | 399 | **399** |
| ModuleCatalog +12 | 359 | **359 (90%)** |
| Materialize created | — | **0** (idempotent) |
| Materialize exists | — | **404** |

Receipt: `data/synth-catalog/receipts/staging-bootstrap-validation.json`

### Operator command

```bash
# With DATABASE_URL + API up:
python scripts/staging_catalog_bootstrap.py \
  --receipt data/synth-catalog/receipts/staging-bootstrap-run.json
# Prefers PATCHHIVE_API_URL / localhost:8000 for materialize-batch
```

Bootstrap fixed to use **API materialize** first (avoids partial SQLAlchemy mapper bootstrap in CLI).

## 2. Rack Builder UX

| Change | Detail |
|--------|--------|
| `module_id` query | Preselects module in placement after gallery Prepare |
| Materialize HP-known | Button on live placement panel → module bulk materialize |
| Module filter | Search/filter placeable modules; sort power-known first |
| Power completeness | Σ +12/−12/+5 and unknown count for current placements |
| Dual-gate panel | Clear hard-fail vs soft-warning language; de-duped warning codes; rail draw/capacity/headroom |
| Gallery Prepare | Navigates to `/racks/new?module_id=` after materialize |

## 3. Scripts

- `scripts/run_bootstrap_validation.py` — structured validation helper
- `scripts/staging_catalog_bootstrap.py` — API-first materialize + overlays
