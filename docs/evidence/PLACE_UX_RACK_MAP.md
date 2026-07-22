# Place UX — visual rack map + existing-rig prepare (2026-07-22)

Follow-on to `CATALOG_PLACE_UX_POLISH.md` / PR #133.

## Changes

| Surface | Detail |
|---------|--------|
| **RackBuilder** | Visual Eurorack **row map**: modules as positioned HP blocks; dashed = power unknown; click block → set start HP; click empty track → set start HP at click |
| **Modules** | **Add to existing** materializes then opens rig picker → `/racks/{id}/edit?module_id=` (Prepare for rig still creates new) |
| **Cases** | URL filter sync (`q`, `format`, `powered`, `min_capacity`); quick chips; placeable/powered/catalog-only status chips on cards |

## Tests

```bash
cd frontend && npm run test:e2e -- -g "module gallery|dual-gate|URL filters|add-to-existing|cases catalog"
```

| Test | Result |
|------|--------|
| gallery search + prepare | pass |
| dual-gate + HP bar + **row map blocks** | pass |
| URL filters + placeable chips | pass |
| **add-to-existing → picker → edit** | pass |
| **cases placeable chips + format URL** | pass |

`tsc --noEmit` clean.

## Operator path

1. `/modules?hp=known` → **Add to existing** → pick rig → placement with module preselected  
2. Or **Prepare for rig** → new case-bound rig  
3. On edit: row map shows occupancy; click gap to set start HP  
4. `/cases?format=eurorack` → Use on new rig  
