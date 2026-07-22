# Automated catalog place-loop simulation & tests (2026-07-22)

## What was added

| Layer | Artifact |
|-------|----------|
| Backend unit/integration | `backend/tests/test_catalog_place_loop_simulation.py` |
| Staging live simulation | `scripts/simulate_catalog_place_loop.py` |
| Bootstrap validation | `scripts/run_bootstrap_validation.py` + receipt |
| Frontend e2e | `mvp.spec.ts` — Prepare→`module_id`, dual-gate panel |

## Backend simulation tests (CI)

```bash
cd backend && .venv/bin/pytest tests/test_catalog_place_loop_simulation.py -q
```

Coverage:

1. **Materialize batch** HP-known only + API parity + idempotent rebatch  
2. **Place** powered modules on case with rails → power headroom **verified**  
3. **Overflow** hard-fail (start_hp past row capacity)  
4. **Connector budget** hard-fail (9 modules on 8-header case)  
5. **Unknown module power** soft incomplete path (not invent)

**Result (local):** `8 passed` (with existing materialize tests)

## Staging live automation

```bash
# API up on :8000
python3 scripts/simulate_catalog_place_loop.py \
  --api http://localhost:8000 \
  --receipt data/synth-catalog/receipts/simulate-catalog-place-loop.json
```

**Result:** `validation.all_ok: true`

| Step | Outcome |
|------|---------|
| health | 200 |
| catalog stats | HP 99% |
| materialize-batch | 0 created / 404 exists |
| create pack on LC3 | 201 |
| compatibility | incomplete (soft) / power rails verified when capacity known |
| overflow probe | 400 hard-fail |

Receipt: `data/synth-catalog/receipts/simulate-catalog-place-loop.json`

## Frontend e2e

```bash
cd frontend && npx playwright test -c tests/ui/playwright.config.ts \
  tests/ui/mvp.spec.ts -g "module gallery|rack builder"
```

| Test | Outcome |
|------|---------|
| Gallery search + Prepare → `/racks/new?module_id=99` | pass |
| Rack edit dual-gate + power completeness | pass |

## Operator matrix

| Command | Purpose |
|---------|---------|
| `pytest tests/test_catalog_place_loop_simulation.py` | Offline dual-gate sim |
| `python3 scripts/simulate_catalog_place_loop.py` | Live staging smoke |
| `python3 scripts/staging_catalog_bootstrap.py` | Rebuild overlays |
| `npx playwright test … mvp.spec.ts` | UI flow |

## CI note

Backend pytest runs in CI (Backend Tests workflow). Staging simulate is **operator/live** (needs running API + data). Playwright runs in frontend Code Quality workflow.
