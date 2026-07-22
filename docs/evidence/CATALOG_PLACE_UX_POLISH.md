# Catalog place UX polish (2026-07-22)

## Intent

After catalog inventory reached product-usable coverage (HP ~99%, placeable ~399, power ~90%), harden the **place loop UX** so operators can:

1. See where they are in Case → Create → Place
2. See row HP occupancy while placing
3. Land from gallery Prepare with a preselected module and smart start HP
4. Share/filter the module gallery via URL
5. Read dual-gate status at a glance on Rigs overview

Fail-closed data rules unchanged: unknown HP/power/depth never invented.

## Changes

| Surface | UX |
|---------|----|
| **RackBuilder** | Step progress (Case / Create / Place); preselect banner for `?module_id=`; per-row HP usage bars; smart start HP (first free gap); dual-gate status chips |
| **Modules** | URL sync (`q`, `brand`, `category`, `hp`, `source`, `status`, `sort`, `page`); quick HP chips; active filter chips; card status chips (placeable / HP unknown / source); primary Prepare CTA |
| **Racks** | Empty-rig placement CTA; compact dual-gate chip summary + expandable detail; generate disabled until modules exist |
| **CSS** | `.step-progress`, `.status-chip`, `.usage-bar`, `.gate-chip-row`, `.placement-cta`, `.module-preselect-banner` |

## Tests

```bash
cd frontend && npm run test:e2e -- -g "module gallery|dual-gate|URL filters"
```

| Test | Result |
|------|--------|
| module gallery supports search filter and placement entry | pass |
| rack builder edit shows dual-gate panel and power completeness | pass (step progress, HP bar 18/84, dual-gate chips) |
| module gallery URL filters and status chips | pass (`?hp=known`, placeable chips) |

`npx tsc --noEmit` clean.

## Operator path

1. `/modules?hp=known` → placeable catalog
2. **Prepare for rig** → materialize → `/racks/new?module_id=N`
3. Choose case → **Create empty rig** → edit with module preselected, start HP at first free gap
4. HP bars + dual-gate chips update on save
5. Rigs overview shows compact dual-gate + Place modules CTA when empty
