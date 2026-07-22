# Multi-module batch place (2026-07-22)

## Intent

Pack several gallery modules onto a case-bound rig in **one save**, with contiguous HP packing and fail-closed unknown widths.

## Implementation

| Piece | Detail |
|-------|--------|
| `frontend/src/lib/placementPack.ts` | `firstFreeStartHp`, `packModulesOntoRows` (L→R, top→bottom, wrap rows) |
| RackBuilder **Batch place** | Multi-select checklist (filtered gallery), plan preview, batch ghosts on row map, single `PUT` with full placement list |
| Single-module path | Unchanged (row + start HP + Add) |

Rules:
- Modules with unknown/non-positive HP are **unplaced** (never invent width)
- Start packing at the current **Row** control value, then wrap other rows
- Already-on-rig modules may still be selected (second instance if API allows; packing uses free gaps)

## Tests

```bash
cd frontend
npx vitest run src/lib/placementPack.test.ts   # 7 passed
npm run test:e2e -- -g "batch place|dual-gate" # 2 passed
```

E2E: select Gamma+Delta → Plan: 2 will pack → Place 2 selected → body `[{id:10,row:0,start:0},{id:11,row:0,start:12}]`.
