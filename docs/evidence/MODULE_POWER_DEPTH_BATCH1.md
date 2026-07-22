# Module power/depth batch 1 (2026-07-22)

## Goal

Bulk OBSERVED +12/−12/+5 and depth for materialised `ModuleCatalog` modules (Track A), plus a durable overlay (Track B lite).

## Method

- Script: `scripts/enrich_module_power_depth_mg.py` (ModularGrid direct HTTP)
- Targets: `modules` with `source=ModuleCatalog` and `power_12v_ma IS NULL` (**393**)
- Apply: fill-null only (`COALESCE`); never invent
- Overlay: `data/synth-catalog/overlays/module-power-depth-v1.json`
- Re-apply: `scripts/apply_module_power_depth_overlay.py`

## Results

| Metric | Value |
|--------|------:|
| Targets | 393 |
| Found (any power or depth) | **344** |
| Not found | 49 |
| With +12 in results | 320 |
| With depth in results | 311 |

### Staging after apply (`source=ModuleCatalog`)

| Metric | Before | After |
|--------|-------:|------:|
| With +12 | 6 | **326** |
| Null +12 | 393 | **73** |
| +12 coverage | ~1.5% | **81.7%** |
| With depth | 6 | **317** |
| Null depth | 393 | **82** |

## Place-loop recheck

| Rack | Power headroom | Soft warnings remaining |
|------|----------------|-------------------------|
| LC3 #6 | +12 **1949/2000** (51 mA) · −12 694/1200 · verified | `MODULE_POWER_UNKNOWN`, `DEPTH_MODULE_UNKNOWN` (residual unenriched) |
| Mantis #7 | +12 649/3000 · −12 251/1100 · +5 35/300 · verified | same soft codes (fewer modules affected) |

Draw on LC3 rose from prior partial pack as more modules gained OBSERVED rails — still under case capacity.

## Artifacts

- `data/synth-catalog/hermes-research/power-depth-batch1.json`
- `data/synth-catalog/hermes-research/power-depth-batch1-results.json`
- `data/synth-catalog/hermes-research/power-depth-batch1-results.filtered.json`
- `data/synth-catalog/overlays/module-power-depth-v1.json`
- `data/synth-catalog/receipts/power-depth-batch1-staging-apply.json`
- `data/synth-catalog/receipts/place-loop-after-power-depth.json`

## Operator re-apply (after materialize-batch)

```bash
# from backend venv with DATABASE_URL set
python scripts/apply_module_power_depth_overlay.py \
  --overlay data/synth-catalog/overlays/module-power-depth-v1.json
```

## Next

- Residual ~73 null power: brand-specific official pages / retry
- Optional: more case rail OBSERVED fills
