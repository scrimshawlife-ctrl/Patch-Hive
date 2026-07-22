# Hermes HP enrichment batch 6 — final residual (2026-07-22)

## Goal

Close the last **14** null-HP `module_catalog` rows after batch 5 (was **394/408 · 96.6%**).

## Applied (10 OBSERVED)

| Slug | HP | Source | Notes |
|------|---:|--------|-------|
| befaco-pip-filter | 4 | ALM MG Pip Filter | Catalog brand mislabeled Befaco (ALM product) |
| befaco-pip-lfo | 4 | ALM MG Pip LFO | same |
| befaco-pip-slope | 4 | ALM MG Pip Slope | same |
| befaco-slicer-v3 | 20 | MG `befaco-befaco-slicer-v3` | Duplicate of BEFACO SLICER V3 row |
| intellijel-aux-mix | 32 | MG Aux Mix 1U | 1U tile |
| intellijel-vcf | 6 | MG `intellijel-%C2%B5vcf` | µVCF unicode slug |
| endorphin-es-shuttle-system-black | 84 | MG Shuttle System | Full system footprint |
| endorphin-es-shuttle-system-golden | 84 | MG Shuttle System | Full system footprint |
| dreadbox-milky-way-1u-silver | 22 | MG Endorphin.es Milky Way 1U | Brand mislabel in seed |
| dreadbox-two-of-cups-black | 6 | MG Endorphin.es Two Of Cups | Brand mislabel in seed |

Policy: fill **width** when OBSERVED even if research seed brand is wrong (document mismatch; do not invent).

## Still null (4) — fail-closed

| Slug | Reason |
|------|--------|
| `doepfer-a-101-5` | No resolvable OBSERVED page (A-101-2 is 8HP; A-101-5 not found) |
| `dreadbox-epsilon` | Pedal / non-eurorack; pages unavailable |
| `dreadbox-taff2-scientific-tremolo` | Guitar pedal; no eurorack HP |
| `instruo-seashell` | Desktop semi-modular system; not a panel-HP module |

## Coverage

| Metric | Before batch 6 | After |
|--------|---------------:|------:|
| HP known | 394 | **404** |
| Unknown | 14 | **4** |
| Coverage | 96.6% | **99.0%** |

## Artifacts

- `data/synth-catalog/hermes-research/hp-enrichment-batch6-final-results.json`
- `data/synth-catalog/receipts/hp-batch6-final-staging-apply.json`
