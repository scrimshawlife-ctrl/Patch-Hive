# Module catalog batch materialize + scale place-loop (2026-07-22)

## Goal

Turn HP-known research catalog into placeable `modules` inventory and prove multi-rack dual-gate placement at scale.

## API

`POST /api/modules/catalog/materialize-batch`

| Query | Default | Meaning |
|-------|---------|---------|
| `hp_known_only` | `true` | Skip null-HP rows (fail-closed) |
| `brand` | — | Optional brand filter |
| `limit` | 500 | Max rows (1–2000) |

Idempotent: existing brand+name → `exists`; new → `created` with `source=ModuleCatalog`. **Never invents** power/depth/I/O.

CLI: `scripts/materialize_module_catalog_batch.py`

## Staging batch result

| Metric | Value |
|--------|------:|
| Scanned (HP known) | 404 |
| Created | **393** |
| Exists | 11 |
| Failed | 0 |
| Rebatch created | 0 |
| Rebatch exists | 404 |

| Table | Count |
|-------|------:|
| `modules` total | **418** |
| `source=ModuleCatalog` | **399** |
| ModuleCatalog with null power | 393 (expected pre power-enrich) |

Receipt: `data/synth-catalog/receipts/materialize-batch-hp-known.json`

## Scale place-loop smoke

### LC3 (case_id=10, rack 6)

- **15** modules, **84/84 HP** packed (prefer modules with known power)
- Power headroom **verified**: +12 449/2000 · −12 194/1200 · +5 0/4000
- Soft warnings: `MODULE_POWER_UNKNOWN`, `DEPTH_MODULE_UNKNOWN` (unenriched catalog rows)

### Mantis (case_id=7, rack 7)

- First pack of **61** modules hard-failed `CONNECTORS_EXCEEDED` (budget **36**) — dual-gate fail-closed ✓
- Retried with **≤36** modules → create OK, `CONNECTORS_OK` (36/36)
- Power headroom **verified**: +12 139/3000 · −12 49/1100 · +5 0/300
- Soft: `DEPTH_MODULE_UNKNOWN` on unenriched modules

Receipt: `data/synth-catalog/receipts/place-loop-scale-smoke.json`

## Tests

- `test_materialize_batch_hp_known_only` — creates only HP-known; idempotent; skips null HP

## Next

Bulk OBSERVED power/depth on ModuleCatalog-sourced modules (393 null power); optional seed overlay so materialize rebuilds stay durable.
