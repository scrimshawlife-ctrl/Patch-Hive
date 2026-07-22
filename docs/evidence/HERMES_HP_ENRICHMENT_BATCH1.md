# Hermes HP enrichment — Batch 1 (2026-07-21)

## Goal

Fill null `module_catalog.hp` for priority brands using manufacturer-confirmed OBSERVED sources (Hermes research pipeline + Firecrawl scrape).

## Targets

`data/synth-catalog/hermes-research/hp-enrichment-batch1.json` — **82** null-HP rows:

Acid Rain Technology, Mutable Instruments, Make Noise, Intellijel, Instruo (+ Noise Engineering if any).

## Acquisition

| Step | Tool |
|------|------|
| Hermes chat session | Attempted with `modular-synth-catalog-research` skill (auth/timeout friction) |
| Production pipeline | `scripts/hermes_hp_enrich_firecrawl.py` using `FIRECRAWL_API_KEY` from Hermes env |
| Method | Official product URL candidates → Firecrawl `/scrape` → HP regex |

### Raw results

| Metric | Count |
|--------|------:|
| Processed | 82 |
| Raw found | 81 |
| Not found | 1 (`Instruo/cèis[2]`) |

File: `data/synth-catalog/hermes-research/hp-enrichment-batch1-results.json`

### Quality filter (fail-closed)

Retailer **search result pages** often return wrong first HP (e.g. many false `2 HP`). Official pages with case widths sometimes emit `84 HP`.

Filter applied → `hp-enrichment-batch1-results.filtered.json`:

| Rule | Dropped |
|------|--------:|
| retailer_search | 47 |
| hp > 42 (case-width leak) | 3 |
| not_found | 1 |
| **Kept (official, 1–42 HP)** | **31** |

## Staging apply

```bash
python scripts/apply_hp_enrichment.py \
  --results data/synth-catalog/hermes-research/hp-enrichment-batch1-results.filtered.json \
  --receipt data/synth-catalog/receipts/hp-batch1-staging-apply.json
```

| Metric | Before | After |
|--------|-------:|------:|
| `module_catalog` HP known | 35 | **66** |
| Coverage | 8.6% | **16.2%** |
| Updated this apply | — | **31** |

Receipts:

- `data/synth-catalog/receipts/hp-batch1-apply.dry-run.json`
- `data/synth-catalog/receipts/hp-batch1-staging-apply.json`

### Verified samples

| Module | HP |
|--------|---:|
| Mutable Instruments Frames | 18 |
| Make Noise Mimeophon | 16 |
| Make Noise Erbe-Verb | 20 |
| Make Noise Optomix | 8 |
| Instruo arbhar | 18 |
| Intellijel Buff Mult | 2 |

## Live API

```text
GET /api/modules/catalog/stats
  known: 66, unknown: 342, coverage_pct: 16.2
```

## Next batches

- Batch 2: Erica Synths, Befaco, Bastl, ADDAC, Expert Sleepers, Endorphin.es
- Improve official URL maps; avoid Perfect Circuit **search** pages (product detail only)
- Re-scrape retailer-dropped set with product URLs only
