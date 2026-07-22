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
