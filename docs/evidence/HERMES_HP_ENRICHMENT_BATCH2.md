# Hermes HP enrichment — Batch 1 retry + Batch 2 (2026-07-21/22)

## Summary

| Stage | Targets | Found (kept) | Staging known after |
|-------|--------:|-------------:|--------------------:|
| Batch 1 (prior) | 82 | 31 official | 66 |
| Batch 1 retry (product pages) | 51 | 20 | 86 |
| **Batch 2** | **301** | **56** | **142** |
| **Coverage** | | | **34.8%** (was 8.6% before Hermes) |

Live: `GET /api/modules/catalog/stats` → known=142, unknown=266, coverage_pct=34.8

## Batch 1 retry

- Targets: retailer-search misreads + not_found from batch 1
- Method: Perfect Circuit **product** URLs + official pages only (no catalogsearch)
- Applied: 20 rows  
- Receipt: `data/synth-catalog/receipts/hp-batch1-retry-staging-apply.json`

Examples: Mysteron 14HP (was false 2), Lúbadh 20HP, Dixie II 8HP, Metropolis 34HP, Constellation 28HP

## Batch 2

- Targets: Erica Synths, Befaco, Bastl, ADDAC, Expert Sleepers, Endorphin.es, Doepfer, Dreadbox, Cwejman, remaining Acid Rain  
- Processed: **301 / 301**  
- Raw found: **56** (all kept under product-page + HP 1–42 filter)  
- Not found: **245** (URL map misses / dead pages / no HP on page)

### Found by brand

| Brand | Hits |
|-------|-----:|
| Bastl Instruments | 27 |
| Befaco | 14 |
| Erica Synths | 9 |
| Expert Sleepers | 5 |
| Endorphin.es | 1 |
| Doepfer / Dreadbox / Cwejman / ADDAC | **0** |

### Apply

```bash
python scripts/apply_hp_enrichment.py \
  --results data/synth-catalog/hermes-research/hp-enrichment-batch2-results.filtered.json \
  --receipt data/synth-catalog/receipts/hp-batch2-staging-apply.json
```

Updated **56** catalog rows. Receipt: `data/synth-catalog/receipts/hp-batch2-staging-apply.json`

## Parallelism note

Single Firecrawl worker completed batch 2 (~39 min). LLM subagents not used (I/O-bound scrape). Brand-sharded workers remain optional for batch 3 (Doepfer/ADDAC/Cwejman URL repair).

## Next (batch 3)

1. **Doepfer**: fix URL map (`doepfer.de/aXXXX.htm` patterns from A-xxx names)  
2. **ADDAC**: product codes ADDAC###  
3. **Cwejman / Dreadbox**: manufacturer site maps  
4. Optional: Perfect Circuit brand browse pages for remaining nulls  
