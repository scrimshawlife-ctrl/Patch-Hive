# Hermes HP enrichment — Batch 3 (2026-07-22)

## Scope

Doepfer, ADDAC System, Cwejman, Dreadbox (null-HP residual after batches 1–2).

**142 targets**, **4 brand-sharded workers** (parallel direct HTTP; Firecrawl credits were 0).

## Method

| Source | Role |
|--------|------|
| Official manufacturer pages | Prefer (Doepfer `a####.htm`, ADDAC product series) |
| Perfect Circuit product URLs | Secondary |
| ModularGrid module pages | Last resort for Cwejman/Dreadbox (403 on brand sites) |
| **Not used** | Firecrawl (HTTP 402 — 0 remaining credits) |

Script: `scripts/hermes_hp_enrich_direct.py`

## Results

| Brand | Processed | Found |
|-------|----------:|------:|
| Doepfer | 50 | **44** |
| ADDAC System | 28 | **26** |
| Cwejman | 29 | **7** |
| Dreadbox | 35 | **1** |
| **Total** | **142** | **78** |

Filtered file: `data/synth-catalog/hermes-research/hp-enrichment-batch3-results.filtered.json`

## Staging apply

```bash
python scripts/apply_hp_enrichment.py \
  --results data/synth-catalog/hermes-research/hp-enrichment-batch3-results.filtered.json \
  --receipt data/synth-catalog/receipts/hp-batch3-staging-apply.json
```

| Metric | Before batch 3 | After |
|--------|---------------:|------:|
| HP known | 142 | **220** |
| Applied this batch | — | **78** |

## Cumulative Hermes program

| Batch | Applied |
|-------|--------:|
| 1 official | 31 |
| 1 retry product pages | 20 |
| 2 Erica/Befaco/Bastl/… | 56 |
| **3 Doepfer/ADDAC/…** | **78** |
| **Σ applied** | **~185** |

Coverage trajectory: 8.6% → 16.2% → 21.1% → 34.8% → **53.9%** after batch 3.

## Residual gaps

- **Dreadbox**: manufacturer 403; only 1 MG hit — need better MG slugs or PDF manuals
- **Cwejman**: squarespace false “2hp” power chip; 7 recovered via MG
- Firecrawl needs top-up for future scrape-heavy batches
