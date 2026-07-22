# Place UX — power rail meters (2026-07-22)

Follow-on to #133 / #134.

## Changes

| Surface | Detail |
|---------|--------|
| **RackBuilder** | **Power rail meters** (+12 / −12 / +5): draw vs case capacity, headroom, tone (green/warn/over); unspecified case rails stay neutral; soft gap callout for modules without +12 |
| **RackBuilder** | **Ghost preview** block on row map for selected module + start HP |
| **Racks overview** | Inventory power chips (draw/capacity per rail when case has rails) |
| **Home** | CTAs: Placeable modules (`/modules?hp=known`), Eurorack cases (`/cases?format=eurorack`) |

Fail-closed: unknown module power not assumed into draw totals; null case rails labeled unspecified.

## Tests

```bash
cd frontend && npm run test:e2e -- -g "module gallery|dual-gate|URL filters|add-to-existing|cases catalog"
```

Dual-gate e2e asserts: Power rail usage region, +12 meter, `40/2000mA`, soft gap for 1 unknown module.

`tsc --noEmit` clean.
