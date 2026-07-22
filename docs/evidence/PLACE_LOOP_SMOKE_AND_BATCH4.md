# Place-loop smoke + HP batch 4 (2026-07-22)

## 1. Staging place-loop smoke (Priority 1)

### Materialize (API)

| Catalog slug | Result | module_id | HP |
|--------------|--------|----------:|---:|
| make-noise-maths | exists | 2 | 20 |
| make-noise-mimeophon | created | 20 | 16 |
| make-noise-optomix | created | 23 | 8 |
| doepfer-a-110 | created | 21 | 10 |
| mutable-instruments-plaits | exists | 1 | 12 |
| erica-synths-pico-drums | created | 22 | 3 |
| intellijel-buff-mult | created | 24 | 2 |

### Rack create (API)

- **Case:** Doepfer A-100LC3 (`case_id=10`, 84 HP)
- **Rack id:** 2 — `Hermes catalog place-loop smoke`
- **Placed:** 7 modules · **71 HP** used (fits in 84)
- **Receipt:** `data/synth-catalog/receipts/place-loop-smoke.json`

### Gate findings (documented)

| Issue | Behavior |
|-------|----------|
| Physical overflow | Muxlicer 16HP at start 71 correctly **hard-failed** (87 > 84) |
| `generation_seed` | Auto hash can exceed signed int32 → **500**; fixed with `& 0x7FFFFFFF` |
| `users` FK | Empty staging users table → need bootstrap user id=1 for rack create |
| Power/depth | Soft warnings for ModuleCatalog-sourced rows (null power/depth) — fail-closed, correct |

## 2. HP batch 4 — Dreadbox + Cwejman

| Brand | Found / residual |
|-------|-----------------:|
| Dreadbox | **29** / 34 |
| Cwejman | **22** / 22 |
| **Total applied** | **51** |

Method: ModularGrid-first direct HTTP (official/PC 403; Firecrawl still at 0 credits).

## 3. Staging coverage after batch 4

| Metric | Value |
|--------|------:|
| HP known | **271 / 408** |
| Coverage | **~66.4%** (was 53.9% after batch 3) |

## Code fix

`backend/core/naming.py` — `hash_string_to_seed` masked to 31-bit signed range.

## 4. Demo-set power enrichment (post-merge continue)

After #120 merge: filled `power_12v_ma` / `power_neg12v_ma` on place-loop modules from ModularGrid (OBSERVED). Depth still null where MG page lacked mm deep token.

| Module | +12 mA | −12 mA |
|--------|-------:|-------:|
| Mimeophon | 100 | 10 |
| Optomix | 25 | 25 |
| A-110 | 90 | 20 |
| Pico DRUMS | 35 | 4 |
| Buff Mult | 4 | 17 |
| Maths / Plaits | already filled | |

Receipt: `data/synth-catalog/receipts/demo-set-power-depth.json`
Staging catalog HP known remains **271/408 (66.4%)**.

## 5. ModuleCatalog power/depth expansion (Muxlicer + residual depth)

After #121: Muxlicer was the only `modules` row still missing power. Filled from ModularGrid **OBSERVED** (cross-checked Perfect Circuit for Muxlicer). Residual `depth_mm` nulls on the other ModuleCatalog place-loop modules filled from the same MG pages. Policy: fill-null only; no invent.

| Module | +12 mA | −12 mA | +5 mA | depth mm | Notes |
|--------|-------:|-------:|------:|---------:|-------|
| Muxlicer | 50 | 5 | 0 | 23 | power+depth (was all null) |
| Mimeophon | 100 | 10 | 0 | 30 | depth + 5V |
| Optomix | 25 | 25 | 0 | 24 | depth + 5V |
| A-110 | 90 | 20 | 0 | 55 | depth + 5V |
| Pico DRUMS | 35 | 4 | 0 | 35 | depth + 5V |
| Buff Mult | 4 | 17 | 0 | 39 | depth + 5V |

### Place-loop recheck

- **Rack id:** 4 — `Hermes place-loop power-depth recheck` (same 7 modules, 71 HP)
- **Module draw:** +12 **369 mA** · −12 **131 mA** · +5 **0 mA**
- **Module-level missing power warnings:** none
- **Residual incomplete:** case rail capacities unspecified on A-100LC3 (fail-closed; headroom not computed)
- **Overflow:** Muxlicer 16HP at start 71 still hard-fails physical fit

Receipts:

- `data/synth-catalog/hermes-research/modulecatalog-power-depth-results.json`
- `data/synth-catalog/receipts/modulecatalog-power-depth-staging-apply.json`
- `data/synth-catalog/receipts/place-loop-power-depth-recheck.json`

Staging: **25/25** `modules` rows have `power_12v_ma`; all 6 `source=ModuleCatalog` rows have power + depth.

## 6. Case rails + catalog source (post-merge continue)

See `docs/evidence/CASE_RAIL_AND_CATALOG_SOURCE.md`.

- **A-100LC3** rails filled (PSU3 2000/1200/4000) → place-loop power headroom **verified** (+12 1631 / −12 1069 / +5 4000 mA).
- **NiftyCASE** rails filled from official OBSERVED peak currents.
- **`module_catalog.source`** column + `SynthCatalogResearch` backfill (408/408).
