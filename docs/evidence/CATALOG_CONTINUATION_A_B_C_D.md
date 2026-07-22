# Catalog continuation A–D (2026-07-22)

Tracks: residual power, rebuild durability, hygiene, light FE.

## A — Residual power/depth

| Metric | Value |
|--------|------:|
| Residual targets | 73 |
| Found (any field) | **36** |
| With +12 | 12 |
| Depth-only | 24 |
| Still null +12 after apply | **61** / 399 ModuleCatalog |

Coverage: ModuleCatalog +12 **81.7% → 84.7%** (338/399).

Overlay v2: `data/synth-catalog/overlays/module-power-depth-v2.json`  
Results: `hermes-research/power-depth-residual*.json`

Remaining null power is largely: passive multiples/blanks without MG draw, expanders, custom panels, unicode/Instruo slug gaps, brand-mismatched rows.

## B — Rebuild durability

| Artifact | Path |
|----------|------|
| HP overlay (404 rows) | `data/synth-catalog/overlays/module-catalog-hp-v1.json` |
| Apply HP | `scripts/apply_module_catalog_hp_overlay.py` |
| Power overlay v1+v2 | `module-power-depth-v1.json`, `module-power-depth-v2.json` |
| Apply power | `scripts/apply_module_power_depth_overlay.py` |
| Bootstrap chain | `scripts/staging_catalog_bootstrap.py` |

### Operator rebuild

```bash
# 1) Import seeds if catalog empty (phase2/phase3)
# 2) From repo with DATABASE_URL:
python scripts/staging_catalog_bootstrap.py
# = HP overlay → materialize-batch → power overlays v1+v2
```

## C — Hygiene (staging applied)

| Change | Detail |
|--------|--------|
| Pip brand | Pip Filter/LFO/Slope → **ALM Busy Circuits** (modules + catalog brand) |
| Residual 4 null HP | `non_eurorack` (Epsilon, Taff2), `desktop` (Seashell), `unresolved` (A-101-5) |
| Duplicate Slicer | `befaco-slicer-v3` → `is_available=duplicate` (prefer `befaco-befaco-slicer-v3`) |

## D — FE + cases

| Change | Detail |
|--------|--------|
| Modules gallery | Stats show `by_source`; cards show **placeable** when HP known + `source` + availability flags |
| Case rails | No new invent; residual powered-null cases remain fail-closed (Pods/Happy Ending/etc. still unspecified in research) |

## Place-loop note

Re-check LC3/Mantis after residual apply: power headroom remains case-capacity constrained; soft `MODULE_POWER_UNKNOWN` only for residual ~61 modules.

## Definition of done (this package)

- [x] Residual power retry + v2 overlay  
- [x] HP overlay + bootstrap script  
- [x] Brand/availability hygiene  
- [x] FE placeable/source badges  
- [ ] Residual 61 power (optional later)  
- [ ] Case rail OBSERVED campaign (optional later)  
