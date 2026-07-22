# Hermes HP enrichment batch 5 — residual nulls (2026-07-22)

## Goal

Close residual `module_catalog` HP gaps after batches 1–4 (was **271/408 · 66.4%**).

## Method

- Extended `scripts/hermes_hp_enrich_direct.py` with **ModularGrid-first** URLs for all residual brands (Erica, Expert Sleepers, Befaco, Endorphin.es, Intellijel, Make Noise, Mutable, Bastl, Acid Rain, Instruo, …).
- Official / Perfect Circuit still tried after MG when brand-specific paths exist.
- **OBSERVED only**; fill-null; never invent. Firecrawl still at 0 credits.

## Results

| Stage | Found / residual | Notes |
|-------|-----------------:|-------|
| Batch 5 main | **119** / 137 | MG-first pass |
| Retry | **+4** | Instruo cèis[2], glōc; Dreadbox Gamma; Make Noise Strega (45 HP semi-modular) |
| **Applied total** | **123** | staging `module_catalog` |

### Coverage

| Metric | Before | After |
|--------|-------:|------:|
| HP known | 271 | **394** |
| Unknown | 137 | **14** |
| Coverage | 66.4% | **96.6%** |

### Remaining null (14) — fail-closed

| Brand | Modules | Reason left null |
|-------|---------|------------------|
| Befaco | Pip Filter/LFO/Slope, Slicer V3 | No resolvable OBSERVED page |
| Doepfer | A-101-5 | Page not found via candidates |
| Dreadbox | Epsilon, Milky Way 1U, Taff2, Two Of Cups (black) | Pedal/alt brand ambiguity |
| Endorphin.es | Shuttle System black/golden | 84 HP **system**, not single module |
| Instruo | Seashell | No page match |
| Intellijel | Aux Mix, µVCF | Slug/µ path unresolved |

Skipped: Dreadbox Two Of Cups via Endorphin.es MG hit (brand mismatch).

## Artifacts

- `scripts/hermes_hp_enrich_direct.py` (MG-first residual brands)
- `data/synth-catalog/hermes-research/hp-enrichment-batch5.json`
- `data/synth-catalog/hermes-research/hp-enrichment-batch5-results.json`
- `data/synth-catalog/hermes-research/hp-enrichment-batch5-results.filtered.json`
- `data/synth-catalog/hermes-research/hp-enrichment-batch5-retry-results.json`
- `data/synth-catalog/receipts/hp-batch5-staging-apply.json`
- `data/synth-catalog/receipts/hp-batch5-retry-staging-apply.json`
